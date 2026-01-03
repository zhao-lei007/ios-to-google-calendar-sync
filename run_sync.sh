#!/bin/bash
# iOS 日历同步到 Google Calendar 启动脚本
# 支持在任意 Mac 上通过 iCloud 运行

# 项目目录（iCloud 路径）
PROJECT_DIR="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/second_brain/obsidian/project/apple_to_goolge"

# 日志文件
LOG_FILE="$PROJECT_DIR/sync.log"

# 锁文件（防止多台 Mac 同时运行）
LOCK_FILE="$PROJECT_DIR/.sync.lock"

# 检查项目目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo "$(date): 项目目录不存在: $PROJECT_DIR" >> "$LOG_FILE"
    exit 1
fi

cd "$PROJECT_DIR"

# 检查锁文件（防止重复运行）
if [ -f "$LOCK_FILE" ]; then
    # 检查锁文件是否超过 30 分钟（可能是上次异常退出）
    LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_FILE") ))
    if [ $LOCK_AGE -lt 1800 ]; then
        echo "$(date): 同步正在其他机器上运行，跳过本次执行" >> "$LOG_FILE"
        exit 0
    else
        echo "$(date): 发现过期锁文件，删除并继续" >> "$LOG_FILE"
        rm -f "$LOCK_FILE"
    fi
fi

# 创建锁文件（包含机器名和时间）
echo "$(hostname) - $(date)" > "$LOCK_FILE"

# 清理函数
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# 记录开始
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "$(date): 开始同步 (机器: $(hostname))" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 激活虚拟环境并运行同步
source "$PROJECT_DIR/venv/bin/activate"
python "$PROJECT_DIR/main.py" >> "$LOG_FILE" 2>&1

# 记录结束
echo "$(date): 同步完成" >> "$LOG_FILE"
