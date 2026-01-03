"""
iOS 日历同步到 Google Calendar 的配置文件

使用方法:
1. 复制此文件并重命名为 config.py
2. 填写你的 iCloud 和 Google 凭证信息
"""

# iCloud 配置
ICLOUD_USERNAME = "your_apple_id@example.com"  # 你的 Apple ID
ICLOUD_APP_PASSWORD = "xxxx-xxxx-xxxx-xxxx"    # Apple 应用专用密码 (在 appleid.apple.com 生成)

# Google Calendar 配置
GOOGLE_CREDENTIALS_FILE = "credentials.json"   # Google API 凭证文件
GOOGLE_TOKEN_FILE = "token.json"               # 授权后自动生成的 token 文件
GOOGLE_CALENDAR_ID = "primary"                 # 使用主日历，或指定特定日历 ID

# 同步配置
SYNC_START_DATE = "2026-01-01"     # 从这个日期开始同步
SYNC_INTERVAL_MINUTES = 5          # 同步间隔（分钟）

# 数据存储
SYNC_STATE_FILE = "sync_state.json"  # 存储同步状态，用于检测变更
