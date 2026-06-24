#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import glob
from collections import defaultdict
from datetime import datetime
import dash
from dash import dcc, html, Output, Input
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CPUDashboard:
    def __init__(self, log_dir='../logs'):
        self.log_dir = log_dir
        self.process_data = {}
        self.monitor_cpu_history = []
        self.monitor_mem_history = []
        self.timestamps = []
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()

    def _csv_sort_key(self, csv_path):
        basename = os.path.basename(csv_path)
        try:
            timestamp = basename.removeprefix('cpu_monitor_').removesuffix('.csv')
            return (datetime.strptime(timestamp, '%Y%m%d_%H%M%S'), os.path.getmtime(csv_path))
        except ValueError:
            return (datetime.fromtimestamp(0), os.path.getmtime(csv_path))

    def _parse_cpu_percent(self, value):
        return max(0.0, min(float(value), 100.0))

    def _parse_float(self, value):
        return float(value)

    def read_latest_csv(self):
        csv_files = glob.glob(os.path.join(self.log_dir, 'cpu_monitor_*.csv'))
        if not csv_files:
            return False

        latest_csv = max(csv_files, key=self._csv_sort_key)

        temp_process_data = defaultdict(lambda: {})
        temp_monitor_data = {}
        ordered_timestamps = []
        timestamp_set = set()

        with open(latest_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamp = (row.get('Timestamp') or '').strip()
                if not timestamp:
                    continue

                if timestamp not in timestamp_set:
                    try:
                        temp_monitor_data[timestamp] = (
                            self._parse_cpu_percent(row.get('Monitor CPU %')),
                            self._parse_float(row.get('Monitor Memory MB'))
                        )
                        ordered_timestamps.append(timestamp)
                        timestamp_set.add(timestamp)
                    except (TypeError, ValueError):
                        pass

                process_name = (row.get('Process Name') or '').strip()
                pid = (row.get('PID') or '').strip()
                if not process_name or not pid:
                    continue

                try:
                    temp_process_data[(process_name, pid)][timestamp] = self._parse_cpu_percent(row.get('CPU %'))
                except (TypeError, ValueError):
                    pass

        if len(ordered_timestamps) > 600:
            ordered_timestamps = ordered_timestamps[-600:]

        self.timestamps = ordered_timestamps
        self.monitor_cpu_history = [temp_monitor_data[ts][0] for ts in self.timestamps]
        self.monitor_mem_history = [temp_monitor_data[ts][1] for ts in self.timestamps]

        self.process_data = {}
        for key in temp_process_data:
            self.process_data[key] = [temp_process_data[key].get(ts, 0) for ts in self.timestamps]

        return bool(self.timestamps)

    def get_top_5_processes(self):
        avg_cpu = {k: sum(v) / len(v) for k, v in self.process_data.items()}
        sorted_procs = sorted(avg_cpu.items(), key=lambda x: x[1], reverse=True)
        filtered = [p for p in sorted_procs if p[0][0].lower() != 'system idle process']
        return filtered[:5]

    def create_top5_chart(self):
        fig = go.Figure()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

        for idx, (proc_id, _) in enumerate(self.get_top_5_processes()):
            data = self.process_data[proc_id]
            fig.add_trace(go.Scatter(
                x=self.timestamps,
                y=data,
                mode='lines',
                name=f'{proc_id[0]} ({proc_id[1]})',
                line=dict(color=colors[idx], width=2),
                hovertemplate='<b>%{fullData.name}</b><br>CPU: %{y:.2f}%<extra></extra>'
            ))

        fig.update_layout(
            title='Top 5 Processes - CPU Usage Over Time',
            xaxis_title='Time (last 10 minutes)',
            yaxis_title='CPU %',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=40, b=40)
        )
        return fig

    def create_monitor_gauges(self):
        avg_cpu = sum(self.monitor_cpu_history) / len(self.monitor_cpu_history) if self.monitor_cpu_history else 0
        avg_mem = sum(self.monitor_mem_history) / len(self.monitor_mem_history) if self.monitor_mem_history else 0

        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=('Monitor CPU %', 'Monitor Memory MB')
        )

        fig.add_trace(
            go.Indicator(
                mode='gauge+number+delta',
                value=avg_cpu,
                title={'text': 'CPU %'},
                domain={'x': [0, 0.5], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': '#1f77b4'},
                    'steps': [
                        {'range': [0, 50], 'color': '#e8f4f8'},
                        {'range': [50, 80], 'color': '#fff3e0'},
                        {'range': [80, 100], 'color': '#ffebee'}
                    ],
                    'threshold': {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': 90}
                }
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Indicator(
                mode='gauge+number+delta',
                value=avg_mem,
                title={'text': 'Memory MB'},
                domain={'x': [0.5, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 500]},
                    'bar': {'color': '#2ca02c'},
                    'steps': [
                        {'range': [0, 200], 'color': '#e8f5e9'},
                        {'range': [200, 350], 'color': '#fff9c4'},
                        {'range': [350, 500], 'color': '#ffebee'}
                    ]
                }
            ),
            row=1, col=2
        )

        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    def create_data_table(self):
        rows = []
        seen = set()

        for (proc_name, pid), cpu_data in sorted(
            self.process_data.items(),
            key=lambda x: (sum(x[1]) / len(x[1])) if x[1] else 0,
            reverse=True
        ):
            if (proc_name, pid) not in seen and proc_name.lower() != 'system idle process':
                rows.append({
                    'Process': proc_name,
                    'PID': pid,
                    'Avg CPU %': f"{sum(cpu_data) / len(cpu_data):.2f}" if cpu_data else "0.00",
                    'Max CPU %': f"{min(max(cpu_data), 100.0):.2f}" if cpu_data else "0.00",
                    'Samples': int(len(cpu_data))
                })
                seen.add((proc_name, pid))
                if len(rows) >= 10:
                    break

        return rows

    def setup_layout(self):
        self.app.layout = html.Div(
            [
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
                html.H1('CPU Monitor Dashboard'),

                html.Div(
                    [
                        html.Div(
                            dcc.Graph(id='top5-chart'),
                            style={'flex': '2', 'minWidth': '600px'}
                        ),
                        html.Div(
                            dcc.Graph(id='monitor-gauges'),
                            style={'flex': '1', 'minWidth': '300px'}
                        )
                    ],
                    style={
                        'display': 'flex',
                        'gap': '20px',
                        'marginBottom': '30px',
                        'flexWrap': 'wrap'
                    }
                ),

                html.Div(
                    [
                        html.H3('Top 10 Processes'),
                        html.Table(
                            id='data-table',
                            style={
                                'width': '100%',
                                'borderCollapse': 'collapse',
                                'marginTop': '10px'
                            }
                        )
                    ]
                )
            ],
            style={
                'maxWidth': '1400px',
                'margin': '20px auto',
                'padding': '20px',
                'fontFamily': 'Arial, sans-serif'
            }
        )

    def setup_callbacks(self):
        @self.app.callback(
            [Output('top5-chart', 'figure'),
             Output('monitor-gauges', 'figure'),
             Output('data-table', 'children')],
            Input('interval-component', 'n_intervals')
        )
        def update_dashboard(n):
            if self.read_latest_csv():
                top5_fig = self.create_top5_chart()
                gauge_fig = self.create_monitor_gauges()

                rows_data = self.create_data_table()
                table_rows = [
                    html.Tr(
                        [html.Th(col, style={'padding': '8px', 'border': '1px solid #ddd', 'textAlign': 'left'})
                         for col in ['Process', 'PID', 'Avg CPU %', 'Max CPU %', 'Samples']]
                    )
                ]
                for row in rows_data:
                    table_rows.append(
                        html.Tr([
                            html.Td(row['Process'], style={'padding': '8px', 'border': '1px solid #ddd'}),
                            html.Td(row['PID'], style={'padding': '8px', 'border': '1px solid #ddd'}),
                            html.Td(row['Avg CPU %'], style={'padding': '8px', 'border': '1px solid #ddd', 'textAlign': 'right'}),
                            html.Td(row['Max CPU %'], style={'padding': '8px', 'border': '1px solid #ddd', 'textAlign': 'right'}),
                            html.Td(row['Samples'], style={'padding': '8px', 'border': '1px solid #ddd', 'textAlign': 'center'}),
                        ])
                    )

                return top5_fig, gauge_fig, table_rows
            else:
                empty_fig = go.Figure()
                empty_fig.add_annotation(text='No data available', showarrow=False)
                return empty_fig, empty_fig, html.Tr(html.Td('No data available'))

    def run(self, debug=False):
        self.app.run(debug=debug, host='127.0.0.1', port=8050)

if __name__ == '__main__':
    dashboard = CPUDashboard()
    dashboard.run(debug=True)
