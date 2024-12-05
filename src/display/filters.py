from datetime import datetime


def to_days(date: datetime):
    return (date - datetime.now()).days


def to_minutes(ttl: int):
    return ttl / 60
