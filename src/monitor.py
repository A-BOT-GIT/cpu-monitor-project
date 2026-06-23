#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import csv
import time
import sys
import os
import subprocess
from datetime import datetime
import signal
import atexit

class CPUMonitor:
    def __init__(self, log_dir=None, interval=5):
        if log_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(os.path.dirname(script_dir), 'logs')
        self.log_dir = log_dir
        self.interval = interval
        self.running = False
        self.csv_file = None
        self.csv_writer = None
        self.pid_file = os.path.join(log_dir, '.monitor.pid')

        os.makedirs(log_dir, exist_ok=True)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self._cleanup)

    def _signal_handler(self, signum, frame):
        self.stop()
        sys.exit(0)

    def _cleanup(self):
        if self.csv_file and not self.csv_file.closed:
            self.csv_file.close()
        if os.path.exists(self.pid_file):
            try:
                os.remove(self.pid_file)
            except:
                pass

    def start(self):
        if self.running:
            print("Monitor already running")
            return

        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(self.log_dir, f'cpu_monitor_{timestamp}.csv')

        self.csv_file = open(csv_path, 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Timestamp', 'Process Name', 'PID', 'CPU %'])
        self.csv_file.flush()

        self.running = True
        print(f"CPU Monitor started. Logging to {csv_path}")

        try:
            while self.running:
                self._sample()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()

    def _sample(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent'])
                if pinfo['cpu_percent'] is not None and pinfo['cpu_percent'] > 0:
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        for pinfo in processes[:50]:
            self.csv_writer.writerow([
                now,
                pinfo['name'],
                pinfo['pid'],
                f"{pinfo['cpu_percent']:.2f}"
            ])

        self.csv_file.flush()

    def stop(self):
        if self.csv_file and not self.csv_file.closed:
            self.csv_file.flush()
            self.csv_file.close()
        self.running = False

def _stop_monitor(log_dir):
    pid_file = os.path.join(log_dir, '.monitor.pid')
    if not os.path.exists(pid_file):
        print("Monitor not running")
        return

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        if psutil.pid_exists(pid):
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                print(f"Stopped monitor process {pid}")
            except ProcessLookupError:
                print(f"Process {pid} no longer exists")
        else:
            print(f"Process {pid} no longer running")
    except Exception as e:
        print(f"Error stopping monitor: {e}")
    finally:
        try:
            os.remove(pid_file)
        except:
            pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python monitor.py [start|stop|_run]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(script_dir), 'logs')

    if cmd == 'start':
        if sys.platform == 'win32':
            monitor_script = os.path.abspath(__file__)
            subprocess.Popen(['python', monitor_script, '_run'],
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            time.sleep(1)
            print("Monitor started in background")
        else:
            subprocess.Popen(['python', os.path.abspath(__file__), '_run'])
            time.sleep(1)
            print("Monitor started in background")
    elif cmd == '_run':
        monitor = CPUMonitor(log_dir=log_dir)
        monitor.start()
    elif cmd == 'stop':
        _stop_monitor(log_dir)
    else:
        print("Unknown command. Use 'start', 'stop', or '_run'")
        sys.exit(1)

if __name__ == '__main__':
    main()
