"""
同步引擎 - 处理增删改检测和同步
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple

from icloud_calendar import ICloudCalendar
from google_calendar import GoogleCalendar


class SyncEngine:
    """日历同步引擎"""

    def __init__(self, icloud: ICloudCalendar, google: GoogleCalendar, state_file: str):
        self.icloud = icloud
        self.google = google
        self.state_file = state_file
        self.sync_state = self._load_state()

    def _load_state(self) -> Dict:
        """加载同步状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载同步状态失败: {e}")

        return {
            'events': {},  # icloud_uid -> {google_id, hash}
            'last_sync': None
        }

    def _save_state(self):
        """保存同步状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存同步状态失败: {e}")

    def sync(self, start_date: datetime) -> Dict[str, int]:
        """
        执行同步

        Args:
            start_date: 同步开始日期

        Returns:
            同步统计 {created, updated, deleted, unchanged}
        """
        stats = {'created': 0, 'updated': 0, 'deleted': 0, 'unchanged': 0, 'errors': 0}

        print(f"\n{'='*50}")
        print(f"开始同步 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")

        # 1. 从 iCloud 获取事件
        print("\n[1/4] 正在从 iCloud 获取事件...")
        icloud_events = self.icloud.get_events(start_date)
        icloud_events_dict = {event['uid']: event for event in icloud_events}

        # 2. 检测需要创建和更新的事件
        print("\n[2/4] 正在检测变更...")
        to_create, to_update = self._detect_changes(icloud_events_dict)

        # 3. 检测需要删除的事件
        to_delete = self._detect_deletions(icloud_events_dict)

        print(f"  - 需要创建: {len(to_create)} 个事件")
        print(f"  - 需要更新: {len(to_update)} 个事件")
        print(f"  - 需要删除: {len(to_delete)} 个事件")

        # 4. 执行同步操作
        print("\n[3/4] 正在执行同步...")

        # 创建新事件
        for uid in to_create:
            event = icloud_events_dict[uid]
            google_id = self.google.create_event(event)
            if google_id:
                self.sync_state['events'][uid] = {
                    'google_id': google_id,
                    'hash': event['hash']
                }
                stats['created'] += 1
            else:
                stats['errors'] += 1

        # 更新事件
        for uid in to_update:
            event = icloud_events_dict[uid]
            google_id = self.sync_state['events'][uid]['google_id']
            if self.google.update_event(google_id, event):
                self.sync_state['events'][uid]['hash'] = event['hash']
                stats['updated'] += 1
            else:
                stats['errors'] += 1

        # 删除事件
        for uid in to_delete:
            google_id = self.sync_state['events'][uid]['google_id']
            if self.google.delete_event(google_id):
                del self.sync_state['events'][uid]
                stats['deleted'] += 1
            else:
                stats['errors'] += 1

        # 计算未变更数量
        stats['unchanged'] = len(icloud_events) - stats['created'] - stats['updated']

        # 5. 保存状态
        print("\n[4/4] 正在保存同步状态...")
        self.sync_state['last_sync'] = datetime.now().isoformat()
        self._save_state()

        # 打印统计
        print(f"\n{'='*50}")
        print("同步完成!")
        print(f"  - 创建: {stats['created']}")
        print(f"  - 更新: {stats['updated']}")
        print(f"  - 删除: {stats['deleted']}")
        print(f"  - 未变更: {stats['unchanged']}")
        if stats['errors'] > 0:
            print(f"  - 错误: {stats['errors']}")
        print(f"{'='*50}\n")

        return stats

    def _detect_changes(self, icloud_events: Dict[str, Dict]) -> Tuple[Set[str], Set[str]]:
        """
        检测需要创建和更新的事件

        Returns:
            (to_create, to_update) - 需要创建和更新的 UID 集合
        """
        to_create = set()
        to_update = set()

        for uid, event in icloud_events.items():
            if uid not in self.sync_state['events']:
                # 新事件
                to_create.add(uid)
            elif self.sync_state['events'][uid]['hash'] != event['hash']:
                # 事件已修改
                to_update.add(uid)

        return to_create, to_update

    def _detect_deletions(self, icloud_events: Dict[str, Dict]) -> Set[str]:
        """
        检测需要删除的事件（在 iCloud 中已删除但在 Google 中还存在）

        Returns:
            需要删除的 UID 集合
        """
        synced_uids = set(self.sync_state['events'].keys())
        current_uids = set(icloud_events.keys())

        return synced_uids - current_uids

    def get_sync_status(self) -> Dict:
        """获取同步状态信息"""
        return {
            'total_synced_events': len(self.sync_state['events']),
            'last_sync': self.sync_state.get('last_sync')
        }


if __name__ == "__main__":
    # 测试代码
    from config import (
        ICLOUD_USERNAME, ICLOUD_APP_PASSWORD,
        GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_ID,
        SYNC_STATE_FILE, SYNC_START_DATE
    )

    # 连接 iCloud
    icloud = ICloudCalendar(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD)
    if not icloud.connect():
        exit(1)

    # 连接 Google Calendar
    google = GoogleCalendar(
        GOOGLE_CREDENTIALS_FILE,
        GOOGLE_TOKEN_FILE,
        GOOGLE_CALENDAR_ID
    )
    if not google.connect():
        exit(1)

    # 执行同步
    engine = SyncEngine(icloud, google, SYNC_STATE_FILE)
    start = datetime.fromisoformat(SYNC_START_DATE)
    engine.sync(start)
