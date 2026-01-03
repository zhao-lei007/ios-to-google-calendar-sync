#!/usr/bin/env python3
"""
iOS 日历同步到 Google Calendar 主程序

功能：
- 从 iCloud 读取日历事件
- 同步到 Google Calendar
- 支持增删改检测
- 支持定时自动同步
"""

import argparse
import signal
import sys
import time
from datetime import datetime

from config import (
    ICLOUD_USERNAME, ICLOUD_APP_PASSWORD,
    GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_ID,
    SYNC_STATE_FILE, SYNC_START_DATE, SYNC_INTERVAL_MINUTES
)
from icloud_calendar import ICloudCalendar
from google_calendar import GoogleCalendar
from sync_engine import SyncEngine


class CalendarSync:
    """日历同步应用"""

    def __init__(self):
        self.icloud = None
        self.google = None
        self.engine = None
        self.running = False

    def setup(self) -> bool:
        """初始化连接"""
        print("正在初始化...")

        # 连接 iCloud
        print("\n[iCloud] 正在连接...")
        self.icloud = ICloudCalendar(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD)
        if not self.icloud.connect():
            print("错误: 无法连接到 iCloud，请检查用户名和应用专用密码")
            return False

        # 连接 Google Calendar
        print("\n[Google] 正在连接...")
        self.google = GoogleCalendar(
            GOOGLE_CREDENTIALS_FILE,
            GOOGLE_TOKEN_FILE,
            GOOGLE_CALENDAR_ID
        )
        if not self.google.connect():
            print("错误: 无法连接到 Google Calendar，请检查凭证文件")
            return False

        # 初始化同步引擎
        self.engine = SyncEngine(self.icloud, self.google, SYNC_STATE_FILE)

        print("\n初始化完成!")
        return True

    def sync_once(self) -> bool:
        """执行一次同步"""
        if not self.engine:
            print("错误: 请先调用 setup() 初始化")
            return False

        try:
            start_date = datetime.fromisoformat(SYNC_START_DATE)
            self.engine.sync(start_date)
            return True
        except Exception as e:
            print(f"同步出错: {e}")
            return False

    def run_daemon(self, interval_minutes: int = None):
        """
        以守护进程模式运行，定时同步

        Args:
            interval_minutes: 同步间隔（分钟）
        """
        if interval_minutes is None:
            interval_minutes = SYNC_INTERVAL_MINUTES

        self.running = True

        # 设置信号处理
        def signal_handler(signum, frame):
            print("\n收到停止信号，正在退出...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print(f"\n开始定时同步模式，间隔: {interval_minutes} 分钟")
        print("按 Ctrl+C 停止\n")

        while self.running:
            self.sync_once()

            if not self.running:
                break

            print(f"下次同步: {interval_minutes} 分钟后")
            print("-" * 30)

            # 等待下次同步
            for _ in range(interval_minutes * 60):
                if not self.running:
                    break
                time.sleep(1)

        print("同步服务已停止")

    def show_status(self):
        """显示同步状态"""
        if not self.engine:
            print("错误: 请先调用 setup() 初始化")
            return

        status = self.engine.get_sync_status()
        print("\n同步状态:")
        print(f"  - 已同步事件数: {status['total_synced_events']}")
        print(f"  - 上次同步时间: {status['last_sync'] or '从未同步'}")


def main():
    parser = argparse.ArgumentParser(
        description='iOS 日历同步到 Google Calendar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py                    # 执行一次同步
  python main.py --daemon           # 以守护进程模式运行（定时同步）
  python main.py --daemon -i 10     # 每 10 分钟同步一次
  python main.py --status           # 显示同步状态
        '''
    )

    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='以守护进程模式运行，定时自动同步'
    )

    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=SYNC_INTERVAL_MINUTES,
        help=f'同步间隔（分钟），默认 {SYNC_INTERVAL_MINUTES} 分钟'
    )

    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='显示同步状态'
    )

    args = parser.parse_args()

    # 创建同步应用
    app = CalendarSync()

    # 初始化
    if not app.setup():
        sys.exit(1)

    # 根据参数执行
    if args.status:
        app.show_status()
    elif args.daemon:
        app.run_daemon(args.interval)
    else:
        app.sync_once()


if __name__ == "__main__":
    main()
