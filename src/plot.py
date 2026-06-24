#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys

class CPUPlotter:
    def __init__(self, log_dir=None):
        if log_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(os.path.dirname(script_dir), 'logs')
        self.log_dir = log_dir
        self.process_data = defaultdict(list)
        self.timestamps = []
        self.lookback_minutes = 10
        self.max_samples = self.lookback_minutes * 60

    def read_csv(self):
        csv_files = [f for f in os.listdir(self.log_dir) if f.startswith('cpu_monitor_') and f.endswith('.csv')]
        if not csv_files:
            print("No CSV files found")
            return False

        latest_csv = sorted(csv_files)[-1]
        csv_path = os.path.join(self.log_dir, latest_csv)

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['Process Name'], row['PID'])
                try:
                    cpu = float(row['CPU %'])
                    self.process_data[key].append(cpu)
                except ValueError:
                    pass

        for key in self.process_data:
            if len(self.process_data[key]) > self.max_samples:
                self.process_data[key] = self.process_data[key][-self.max_samples:]

        return True

    def get_top_5_processes(self):
        avg_cpu = {key: sum(vals) / len(vals) for key, vals in self.process_data.items()}
        top_5 = sorted(avg_cpu.items(), key=lambda x: x[1], reverse=True)[:5]
        return [k for k, v in top_5]

    def plot(self):
        if not self.read_csv():
            print("Failed to read CSV data")
            return

        top_5 = self.get_top_5_processes()
        if not top_5:
            print("No process data available")
            return

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle('Top 5 Processes - CPU Usage Over Time')
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('CPU %')
        ax.grid(True, alpha=0.3)

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for idx, (proc_name, pid) in enumerate(top_5):
            data = self.process_data[(proc_name, pid)]
            x = range(len(data))
            ax.plot(x, data, label=f'{proc_name} (PID: {pid})', color=colors[idx], linewidth=2)

        ax.legend(loc='upper left', fontsize=9)
        plt.tight_layout()
        plt.show()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(script_dir), 'logs')

    plotter = CPUPlotter(log_dir=log_dir)
    plotter.plot()

if __name__ == '__main__':
    main()
