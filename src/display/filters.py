from datetime import datetime


def to_days(date):
    return (date - datetime.now()).days


def to_minutes(ttl):
    return ttl / 60
