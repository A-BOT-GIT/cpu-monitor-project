#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt

class CPUPlotter:
    def __init__(self, log_dir='../logs'):
        self.log_dir = log_dir
        self.process_data = defaultdict(list)
        self.max_samples = 600

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

    def get_top_5(self):
        avg_cpu = {k: sum(v) / len(v) for k, v in self.process_data.items()}
        return sorted(avg_cpu.items(), key=lambda x: x[1], reverse=True)[:5]

    def plot(self):
        if not self.read_csv():
            return

        top_5 = self.get_top_5()
        if not top_5:
            print("No process data available")
            return

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle('Top 5 Processes - CPU Usage Over Time')
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('CPU %')
        ax.grid(True, alpha=0.3)

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for idx, (proc_id, _) in enumerate(top_5):
            data = self.process_data[proc_id]
            ax.plot(range(len(data)), data, label=f'{proc_id[0]} (PID: {proc_id[1]})', color=colors[idx])

        ax.legend(loc='upper left', fontsize=9)
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    plotter = CPUPlotter()
    plotter.plot()
