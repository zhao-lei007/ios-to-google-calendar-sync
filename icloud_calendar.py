"""
iCloud CalDAV 日历读取模块
"""

import caldav
from icalendar import Calendar
from datetime import datetime, timedelta
from dateutil import tz
import hashlib
from typing import List, Dict, Optional


class ICloudCalendar:
    """iCloud 日历客户端"""

    CALDAV_URL = "https://caldav.icloud.com"

    def __init__(self, username: str, app_password: str):
        self.username = username
        self.app_password = app_password
        self.client = None
        self.principal = None

    def connect(self) -> bool:
        """连接到 iCloud CalDAV 服务"""
        try:
            self.client = caldav.DAVClient(
                url=self.CALDAV_URL,
                username=self.username,
                password=self.app_password
            )
            self.principal = self.client.principal()
            print(f"成功连接到 iCloud 日历")
            return True
        except Exception as e:
            print(f"连接 iCloud 失败: {e}")
            return False

    def get_calendars(self) -> List[caldav.Calendar]:
        """获取所有日历"""
        if not self.principal:
            raise Exception("未连接到 iCloud，请先调用 connect()")
        return self.principal.calendars()

    def get_events(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict]:
        """
        获取指定日期范围内的所有事件

        Args:
            start_date: 开始日期
            end_date: 结束日期，默认为 start_date + 1年

        Returns:
            事件列表
        """
        if not end_date:
            end_date = start_date + timedelta(days=365)

        calendars = self.get_calendars()
        all_events = []

        for calendar in calendars:
            try:
                calendar_name = calendar.name
                print(f"正在读取日历: {calendar_name}")

                events = calendar.date_search(
                    start=start_date,
                    end=end_date,
                    expand=True
                )

                for event in events:
                    try:
                        event_data = self._parse_event(event, calendar_name)
                        if event_data:
                            all_events.append(event_data)
                    except Exception as e:
                        print(f"解析事件失败: {e}")
                        continue

            except Exception as e:
                print(f"读取日历 {calendar.name} 失败: {e}")
                continue

        print(f"共获取到 {len(all_events)} 个事件")
        return all_events

    def _parse_event(self, event, calendar_name: str) -> Optional[Dict]:
        """解析 CalDAV 事件为字典格式"""
        try:
            cal = Calendar.from_ical(event.data)

            for component in cal.walk():
                if component.name == "VEVENT":
                    # 获取基本信息
                    uid = str(component.get('uid', ''))
                    summary = str(component.get('summary', '无标题'))
                    description = str(component.get('description', '')) if component.get('description') else ''
                    location = str(component.get('location', '')) if component.get('location') else ''

                    # 获取时间
                    dtstart = component.get('dtstart')
                    dtend = component.get('dtend')

                    if not dtstart:
                        return None

                    start_dt = dtstart.dt
                    end_dt = dtend.dt if dtend else None

                    # 判断是否为全天事件
                    is_all_day = not isinstance(start_dt, datetime)

                    # 转换时间格式
                    if is_all_day:
                        start_str = start_dt.isoformat()
                        end_str = end_dt.isoformat() if end_dt else start_str
                    else:
                        # 确保有时区信息
                        if start_dt.tzinfo is None:
                            start_dt = start_dt.replace(tzinfo=tz.tzlocal())
                        if end_dt and end_dt.tzinfo is None:
                            end_dt = end_dt.replace(tzinfo=tz.tzlocal())

                        start_str = start_dt.isoformat()
                        end_str = end_dt.isoformat() if end_dt else start_str

                    # 获取最后修改时间（用于检测变更）
                    last_modified = component.get('last-modified')
                    if last_modified:
                        last_modified_str = last_modified.dt.isoformat()
                    else:
                        last_modified_str = None

                    # 生成事件哈希（用于检测变更）
                    event_hash = self._generate_event_hash(
                        uid, summary, description, location,
                        start_str, end_str, is_all_day
                    )

                    return {
                        'uid': uid,
                        'summary': summary,
                        'description': description,
                        'location': location,
                        'start': start_str,
                        'end': end_str,
                        'is_all_day': is_all_day,
                        'calendar_name': calendar_name,
                        'last_modified': last_modified_str,
                        'hash': event_hash
                    }

        except Exception as e:
            print(f"解析事件数据失败: {e}")
            return None

        return None

    def _generate_event_hash(self, uid: str, summary: str, description: str,
                            location: str, start: str, end: str, is_all_day: bool) -> str:
        """生成事件内容的哈希值，用于检测变更"""
        content = f"{uid}|{summary}|{description}|{location}|{start}|{end}|{is_all_day}"
        return hashlib.md5(content.encode()).hexdigest()


if __name__ == "__main__":
    # 测试代码
    from config import ICLOUD_USERNAME, ICLOUD_APP_PASSWORD, SYNC_START_DATE
    from datetime import datetime

    client = ICloudCalendar(ICLOUD_USERNAME, ICLOUD_APP_PASSWORD)
    if client.connect():
        start = datetime.fromisoformat(SYNC_START_DATE)
        events = client.get_events(start)
        for event in events[:5]:  # 只打印前5个
            print(f"- {event['summary']} ({event['start']})")
