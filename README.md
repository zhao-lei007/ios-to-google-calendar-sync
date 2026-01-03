# iOS Calendar to Google Calendar Sync

自动将 iOS (iCloud) 日历同步到 Google Calendar 的工具。

## 功能

- 从 iCloud CalDAV 读取所有日历事件
- 同步到 Google Calendar 主日历
- 支持增量同步：新增、修改、删除
- 支持定时自动同步
- 支持多台 Mac 共享使用（通过 iCloud）
- macOS 开机自启动

## 前置要求

- Python 3.9+
- macOS
- iCloud 账号（Apple ID）
- Google Cloud 项目和 Calendar API 凭证

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/zhao-lei007/ios-to-google-calendar-sync.git
cd ios-to-google-calendar-sync
```

### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置凭证

#### 3.1 获取 Google Calendar API 凭证

1. 打开 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目
3. 启用 Google Calendar API
4. 创建 OAuth 2.0 凭证（Desktop App 类型）
5. 下载凭证文件，保存为项目目录下的 `credentials.json`

#### 3.2 获取 Apple 应用专用密码

1. 访问 [Apple ID 管理页面](https://appleid.apple.com/)
2. 登录后进入「登录和安全」→「应用专用密码」
3. 生成新的应用专用密码

#### 3.3 创建配置文件

```bash
cp config.example.py config.py
```

编辑 `config.py`，填入你的信息：

```python
ICLOUD_USERNAME = "your_apple_id@example.com"
ICLOUD_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"
SYNC_START_DATE = "2026-01-01"  # 修改为你想开始同步的日期
```

### 4. 首次运行

```bash
python main.py
```

首次运行会打开浏览器要求 Google 账号授权，授权后会自动保存 token。

## 使用方法

### 手动同步一次

```bash
python main.py
```

### 以守护进程模式运行（定时同步）

```bash
# 默认每 5 分钟同步一次
python main.py --daemon

# 自定义间隔（每 10 分钟）
python main.py --daemon -i 10
```

### 查看同步状态

```bash
python main.py --status
```

## 开机自启动（macOS）

运行安装脚本：

```bash
./install_on_new_mac.sh
```

这会配置 macOS LaunchAgent，实现：
- 每次登录时自动同步一次
- 每天 8:00、12:00、18:00、22:00 定时同步

### 管理命令

```bash
# 停止服务
launchctl unload ~/Library/LaunchAgents/com.zhaolei.calendar-sync.plist

# 启动服务
launchctl load ~/Library/LaunchAgents/com.zhaolei.calendar-sync.plist

# 立即触发一次同步
launchctl start com.zhaolei.calendar-sync
```

### 查看日志

```bash
cat sync.log
```

## 多台 Mac 共享

如果项目放在 iCloud 目录中，可以在多台 Mac 上使用：

1. 确保 iCloud 已同步项目文件夹
2. 在每台 Mac 上运行 `./install_on_new_mac.sh`

脚本使用锁文件机制防止多台 Mac 同时运行同步任务。

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主程序入口 |
| `icloud_calendar.py` | iCloud CalDAV 日历读取模块 |
| `google_calendar.py` | Google Calendar API 操作模块 |
| `sync_engine.py` | 同步引擎，处理增删改检测 |
| `config.py` | 配置文件（需自行创建，包含敏感信息）|
| `config.example.py` | 配置文件模板 |
| `run_sync.sh` | 启动脚本（供 LaunchAgent 调用）|
| `install_on_new_mac.sh` | 新 Mac 安装脚本 |

## 注意事项

- `credentials.json`、`token.json`、`config.py` 包含敏感信息，已在 `.gitignore` 中排除
- 首次运行需要网络连接进行 Google 授权
- iCloud CalDAV 有访问频率限制，不建议设置过于频繁的同步间隔

## License

MIT
