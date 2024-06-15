def format_mask_email(email):
    """
    이메일 주소를 마스킹합니다.

    :param email: 마스킹할 이메일 주소
    :return: 마스킹된 이메일 주소
    """
    if '@' not in email:
        raise ValueError("Invalid email address")

    local_part, domain_part = email.split('@')
    if len(local_part) <= 2:
        masked_local = local_part[0] + "*" * (len(local_part) - 1)
    else:
        masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]

    masked_email = masked_local + "@" + domain_part
    return masked_email

def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    try:
        return dt.strftime(fmt)
    except Exception as e:
        print(e)
        return None
