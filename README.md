# CPU Monitor - Windows 10 专用CPU占用监控工具

一个轻量级的Windows CPU监控脚本，用于实时监控系统进程CPU占用情况。

## 功能特性

### 📊 监控功能
- 实时监控系统进程CPU占用百分比
- 按CPU占用排序，记录TOP 50进程
- 自动记录时间戳、进程名、PID、CPU占用%
- 导出为CSV格式便于后续分析
- 支持后台运行
- 支持手动启动/停止
- **采样间隔：1秒（超高精度）**
- **自我监控：记录monitor.py自身CPU和内存占用**

### 🎨 Web仪表板 (v1.2.0+)
- Plotly + Dash 专业级Web UI
- 实时曲线图：Top 5进程CPU占用趋势
- 资源仪表盘：Monitor进程CPU%和内存占用
- 数据表格：Top 10进程详细信息
- 1秒级自动刷新，流式数据更新
- 访问地址：http://localhost:8050

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

### 🎨 方式零：Web实时仪表板（推荐）

**启动仪表板：**
```bash
python src/dashboard.py
```

然后访问浏览器：`http://localhost:8050`

**仪表板功能：**
- 📈 Top 5进程CPU占用曲线图（实时更新）
- 🔧 Monitor进程资源占用仪表盘（CPU%、内存MB）
- 📊 Top 10进程数据表格（含时间戳）
- ⚡ 1秒级自动刷新

**停止仪表板：**
```bash
Ctrl + C
```

---

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

**启动仪表板（新增）：**
```cmd
python src/dashboard.py
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

### Monitor配置
在 `src/monitor.py` 中修改以下参数：

- `interval`: 采样间隔（秒），**默认为1秒**（v1.1.0+）
- `log_dir`: 日志目录，默认为 `../logs`

### Dashboard配置
在 `src/dashboard.py` 中修改以下参数：

- `app.run_server(host='localhost', port=8050)`: 服务器地址和端口
- `TOP_N = 5`: 曲线图显示的进程数（默认Top 5）
- `HISTORY_SIZE = 600`: 历史数据点数（默认10分钟 = 600个1秒采样点）

## 项目结构

```
cpu-monitor-project/
├── src/
│   ├── monitor.py          # 主监控脚本（1秒采样、自我监控）
│   ├── dashboard.py        # Web仪表板（Plotly+Dash）
│   └── plot.py             # 静态图表生成（向后兼容）
├── logs/                   # 监控数据存储目录
├── start.bat               # 启动脚本（批处理）
├── start.ps1               # 启动脚本（PowerShell）
├── stop.bat                # 停止脚本（批处理）
├── stop.ps1                # 停止脚本（PowerShell）
├── requirements.txt        # Python依赖
├── PR_DESCRIPTION.md       # v1.2.0更新说明
└── README.md               # 本文件
```

## 技术细节

### Monitor功能
- 使用 `psutil` 库获取进程信息
- **1秒采样间隔**（v1.1.0+，从原来的5秒优化）
- 每次采样记录CPU占用>0的TOP 50进程
- 记录Monitor自身CPU占用和内存占用
- 每100次采样输出平均资源占用
- 通过PID文件实现启停控制
- 支持Ctrl+C中断运行

### Dashboard功能
- Plotly：交互式图表库，支持放大、缩小、导出
- Dash：Web应用框架，提供响应式UI
- 实时流式更新：自动读取最新CSV数据
- Dash Mantine Components：现代化UI组件库

## 依赖

- Python 3.6+
- psutil >= 5.9.0
- matplotlib >= 3.5.0（可选，用于plot.py）
- plotly >= 5.0（用于dashboard）
- dash >= 2.0（用于dashboard）

## 许可证

MIT
