from __future__ import annotations

from datetime import datetime, timedelta, time as dt_time
from zoneinfo import ZoneInfo


WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def now_in_tz(tz_name: str) -> datetime:
    """Retorna agora no timezone informado."""
    return datetime.now(ZoneInfo(tz_name))


def parse_time_hhmm(value: str) -> dt_time:
    """Converte HH:MM para objeto time."""
    hour, minute = value.split(":")
    return dt_time(hour=int(hour), minute=int(minute))


def next_datetime_for(weekday: str, time_str: str, tz_name: str, base: datetime) -> datetime:
    """Calcula proxima ocorrencia do dia/horario informado."""
    target_time = parse_time_hhmm(time_str)
    weekday_index = WEEKDAYS.index(weekday)
    days_ahead = (weekday_index - base.weekday()) % 7
    candidate = datetime.combine(
        (base + timedelta(days=days_ahead)).date(),
        target_time,
        tzinfo=ZoneInfo(tz_name),
    )
    if candidate <= base:
        candidate += timedelta(days=7)
    return candidate
