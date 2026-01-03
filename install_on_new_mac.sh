#!/bin/bash
# 在新的 Mac 上安装日历同步服务
# 使用方法: 在新 Mac 上运行此脚本

PROJECT_DIR="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/second_brain/obsidian/project/apple_to_goolge"
PLIST_FILE="com.zhaolei.calendar-sync.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "=== iOS 日历同步服务安装脚本 ==="
echo ""

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在，请确保 iCloud 已同步完成"
    echo "路径: $PROJECT_DIR"
    exit 1
fi

# 创建 LaunchAgents 目录（如果不存在）
mkdir -p "$LAUNCH_AGENTS_DIR"

# 创建 LaunchAgent plist 文件（使用当前用户的路径）
cat > "$LAUNCH_AGENTS_DIR/$PLIST_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zhaolei.calendar-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>PLACEHOLDER_PROJECT_DIR/run_sync.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>18</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>22</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
    <key>StandardOutPath</key>
    <string>PLACEHOLDER_PROJECT_DIR/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>PLACEHOLDER_PROJECT_DIR/launchd_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

# 替换占位符为实际路径
sed -i '' "s|PLACEHOLDER_PROJECT_DIR|$PROJECT_DIR|g" "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "1. LaunchAgent 配置文件已创建"

# 卸载旧的（如果存在）
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_FILE" 2>/dev/null

# 加载新的
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "2. 服务已加载"

# 检查状态
if launchctl list | grep -q "calendar-sync"; then
    echo ""
    echo "=== 安装成功! ==="
    echo ""
    echo "服务已配置为:"
    echo "  - 每次登录时自动运行"
    echo "  - 每天 8:00, 12:00, 18:00, 22:00 定时运行"
    echo ""
    echo "手动运行命令:"
    echo "  $PROJECT_DIR/run_sync.sh"
    echo ""
    echo "查看日志:"
    echo "  cat $PROJECT_DIR/sync.log"
else
    echo "错误: 服务加载失败"
    exit 1
fi
