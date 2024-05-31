def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    try:
        return dt.strftime(fmt)
    except Exception as e:
        print(e)
        return None
