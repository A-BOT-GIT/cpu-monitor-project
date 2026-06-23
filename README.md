# CPU Monitor - Windows 10 专用CPU占用监控工具

一个轻量级的Windows CPU监控脚本，用于实时监控系统进程CPU占用情况。

## 功能特性

- 实时监控系统进程CPU占用百分比
- 按CPU占用排序，记录TOP 50进程
- 自动记录时间戳、进程名、PID、CPU占用%
- 导出为CSV格式便于后续分析
- 支持后台运行
- 支持手动启动/停止

## 安装

### 1. 安装Python依赖

```cmd
pip install -r requirements.txt
```

或者使用PowerShell：

```powershell
pip install -r requirements.txt
```

## 使用方法

### 方式一：使用批处理脚本（推荐Windows用户）

**启动监控：**
```cmd
start.bat
```

**停止监控：**
```cmd
stop.bat
```

### 方式二：使用PowerShell脚本

**启动监控：**
```powershell
.\start.ps1
```

**停止监控：**
```powershell
.\stop.ps1
```

### 方式三：命令行方式

**启动监控：**
```cmd
python src/monitor.py start
```

**停止监控：**
```cmd
python src/monitor.py stop
```

## 数据存储

监控数据自动保存到 `logs/` 文件夹下，文件名格式为：
```
cpu_monitor_YYYYMMDD_HHMMSS.csv
```

### CSV数据格式

| 列名 | 说明 |
|------|------|
| Timestamp | 采样时间 |
| Process Name | 进程名称 |
| PID | 进程ID |
| CPU % | CPU占用百分比 |

## 配置

在 `src/monitor.py` 中修改以下参数：

- `interval`: 采样间隔（秒），默认为5秒
- `log_dir`: 日志目录，默认为 `../logs`

## 项目结构

```
cpu-monitor-project/
├── src/
│   └── monitor.py          # 主监控脚本
├── logs/                   # 监控数据存储目录
├── start.bat               # 启动脚本（批处理）
├── start.ps1               # 启动脚本（PowerShell）
├── stop.bat                # 停止脚本（批处理）
├── stop.ps1                # 停止脚本（PowerShell）
├── requirements.txt        # Python依赖
└── README.md               # 本文件
```

## 技术细节

- 使用 `psutil` 库获取进程信息
- 每次采样记录CPU占用>0的TOP 50进程
- 通过PID文件实现启停控制
- 支持Ctrl+C中断运行

## 依赖

- Python 3.6+
- psutil >= 5.9.0

## 许可证

MIT
