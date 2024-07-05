from datetime import datetime


def to_days(date):
    return (date - datetime.now()).days
