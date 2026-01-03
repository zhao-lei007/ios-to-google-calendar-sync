"""
Google Calendar API 操作模块
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Google Calendar API 权限范围
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendar:
    """Google Calendar 客户端"""

    def __init__(self, credentials_file: str, token_file: str, calendar_id: str = 'primary'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.calendar_id = calendar_id
        self.service = None
        self.creds = None

    def connect(self) -> bool:
        """连接到 Google Calendar API"""
        try:
            # 尝试加载已保存的凭证
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

            # 如果凭证无效或不存在，进行认证
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("正在刷新 Google 凭证...")
                    self.creds.refresh(Request())
                else:
                    print("正在进行 Google 授权，请在浏览器中完成登录...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # 保存凭证供下次使用
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
                print(f"凭证已保存到 {self.token_file}")

            # 创建服务
            self.service = build('calendar', 'v3', credentials=self.creds)
            print("成功连接到 Google Calendar")
            return True

        except Exception as e:
            print(f"连接 Google Calendar 失败: {e}")
            return False

    def get_events(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict]:
        """
        获取指定日期范围内的事件

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            事件列表
        """
        if not self.service:
            raise Exception("未连接到 Google Calendar，请先调用 connect()")

        try:
            time_min = start_date.isoformat() + 'Z' if start_date.tzinfo is None else start_date.isoformat()

            params = {
                'calendarId': self.calendar_id,
                'timeMin': time_min,
                'singleEvents': True,
                'orderBy': 'startTime',
                'maxResults': 2500
            }

            if end_date:
                time_max = end_date.isoformat() + 'Z' if end_date.tzinfo is None else end_date.isoformat()
                params['timeMax'] = time_max

            events_result = self.service.events().list(**params).execute()
            events = events_result.get('items', [])

            return events

        except HttpError as e:
            print(f"获取 Google 日历事件失败: {e}")
            return []

    def create_event(self, event_data: Dict) -> Optional[str]:
        """
        创建新事件

        Args:
            event_data: 事件数据

        Returns:
            创建的事件 ID
        """
        if not self.service:
            raise Exception("未连接到 Google Calendar")

        try:
            google_event = self._convert_to_google_event(event_data)
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=google_event
            ).execute()

            event_id = created_event.get('id')
            print(f"创建事件成功: {event_data['summary']} (ID: {event_id})")
            return event_id

        except HttpError as e:
            print(f"创建事件失败: {e}")
            return None

    def update_event(self, event_id: str, event_data: Dict) -> bool:
        """
        更新事件

        Args:
            event_id: Google 事件 ID
            event_data: 新的事件数据

        Returns:
            是否成功
        """
        if not self.service:
            raise Exception("未连接到 Google Calendar")

        try:
            google_event = self._convert_to_google_event(event_data)
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=google_event
            ).execute()

            print(f"更新事件成功: {event_data['summary']}")
            return True

        except HttpError as e:
            print(f"更新事件失败: {e}")
            return False

    def delete_event(self, event_id: str) -> bool:
        """
        删除事件

        Args:
            event_id: Google 事件 ID

        Returns:
            是否成功
        """
        if not self.service:
            raise Exception("未连接到 Google Calendar")

        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            print(f"删除事件成功: {event_id}")
            return True

        except HttpError as e:
            if e.resp.status == 404:
                print(f"事件已不存在: {event_id}")
                return True
            print(f"删除事件失败: {e}")
            return False

    def find_event_by_icloud_uid(self, icloud_uid: str) -> Optional[Dict]:
        """
        通过 iCloud UID 查找 Google Calendar 中的对应事件

        Args:
            icloud_uid: iCloud 事件的 UID

        Returns:
            找到的事件，或 None
        """
        if not self.service:
            raise Exception("未连接到 Google Calendar")

        try:
            # 使用 extendedProperties 搜索
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                privateExtendedProperty=f'icloud_uid={icloud_uid}',
                singleEvents=True,
                maxResults=1
            ).execute()

            events = events_result.get('items', [])
            return events[0] if events else None

        except HttpError as e:
            print(f"搜索事件失败: {e}")
            return None

    def _convert_to_google_event(self, event_data: Dict) -> Dict:
        """将 iCloud 事件数据转换为 Google Calendar 格式"""
        google_event = {
            'summary': event_data['summary'],
            'description': event_data.get('description', ''),
            'location': event_data.get('location', ''),
            'extendedProperties': {
                'private': {
                    'icloud_uid': event_data['uid'],
                    'icloud_hash': event_data.get('hash', ''),
                    'source_calendar': event_data.get('calendar_name', '')
                }
            }
        }

        # 设置时间
        if event_data.get('is_all_day'):
            google_event['start'] = {'date': event_data['start'][:10]}
            google_event['end'] = {'date': event_data['end'][:10]}
        else:
            google_event['start'] = {
                'dateTime': event_data['start'],
                'timeZone': 'Asia/Shanghai'
            }
            google_event['end'] = {
                'dateTime': event_data['end'],
                'timeZone': 'Asia/Shanghai'
            }

        return google_event


if __name__ == "__main__":
    # 测试代码
    from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE, GOOGLE_CALENDAR_ID

    client = GoogleCalendar(
        GOOGLE_CREDENTIALS_FILE,
        GOOGLE_TOKEN_FILE,
        GOOGLE_CALENDAR_ID
    )

    if client.connect():
        from datetime import datetime
        events = client.get_events(datetime(2026, 1, 1))
        print(f"找到 {len(events)} 个事件")
        for event in events[:5]:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {event.get('summary', '无标题')} ({start})")
