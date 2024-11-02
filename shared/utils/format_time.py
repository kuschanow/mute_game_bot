from datetime import timedelta


def format_time(time: timedelta) -> str:
    return str(time).replace(' day,', '').replace(' days,', '')[:-3]
