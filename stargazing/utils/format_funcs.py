def format_pomodoro_time(seconds: int, show_seconds=True) -> str:
    s = seconds
    m = s // 60
    s -= m * 60

    if not show_seconds:
        return m

    if m:
        format_s = '0' + str(s) if s < 10 else s
        return f"{m}:{format_s}"
    return s


def format_project_time(seconds: int, show_seconds=False) -> str:
    s = seconds
    h = s // 3600
    m = (s - h * 3600) // 60

    if show_seconds:
        s -= h * 3600 + m * 60
        return f"{h}h {m}m {s}s"
    return f"{h}h {m}m"
