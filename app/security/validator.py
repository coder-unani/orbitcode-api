import re
from app.config.settings import settings


def validate_usercode(usercode):
    if not usercode:
        return "VALID_USER_CODE_REQUIRE_ERR"
    # 유효한 회원 유형인지 확인
    if usercode in settings.USER_CODE_ALLOW:
        return "VALID_USER_CODE_SUCC"
    else:
        return "VALID_USER_CODE_ERR"


def validate_email(email):
    # 이메일 주소의 패턴을 정의
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # 이메일 주소 필수 입력
    if not email:
        return "VALID_EMAIL_REQUIRE_ERR"
    # 이메일 주소 길이 검사
    if len(email) < settings.USER_EMAIL_LENGTH_MIN or len(email) > settings.USER_EMAIL_LENGTH_MAX:
        return "VALID_EMAIL_LENGTH_ERR"
    # 이메일 주소 공백 검사
    if settings.USER_EMAIL_ALLOW_SPACE and ' ' in email:
        return "VALID_EMAIL_INCLUDE_SPACE_ERR"
    # 정규식을 사용하여 이메일 주소 유효성 검사
    if not re.match(pattern, email):
        return "VALID_EMAIL_PATTERN_ERR"
    # 모든 조건 통과
    return "VALID_EMAIL_SUCC"


def validate_nickname(nickname):
    # 닉네임 필수 입력
    if not nickname:
        return "VALID_NICK_REQUIRE_ERR"
    # 닉네임 길이 제한
    if len(nickname) < settings.USER_NICKNAME_LENGTH_MIN or len(nickname) > settings.USER_NICKNAME_LENGTH_MAX:
        return "VALID_NICK_LENGTH_ERR"
    # 닉네임 공백 포함 여부
    if settings.USER_EMAIL_ALLOW_SPACE and ' ' in nickname:
        return "VALID_NICK_INCLUDE_SPACE_ERR"
    # 모든 조건 통과
    return "VALID_NICK_SUCC"


def validate_password(password):
    # 5. 공백 입력 불가
    if settings.USER_PASSWORD_INCLUDE_SPACE and ' ' in password:
        return "VALID_PWD_INCLUDE_SPACE_ERR"

    # 1. 8자리 이상 최대 22자리
    if len(password) < settings.USER_PASSWORD_LENGTH_MIN or len(password) > settings.USER_PASSWORD_LENGTH_MAX:
        return "VALID_PWD_LENGTH_ERR"

    # 2. 대소문자 상관없이 문자열 반드시 포함
    if settings.USER_PASSWORD_INCLUDE_WORD and not re.search(r'[a-zA-Z]', password):
        return "VALID_PWD_NOT_INC_WORD_ERR"

    # 3. 숫자 반드시 포함
    if settings.USER_PASSWORD_INCLUDE_NUMBER and not re.search(r'\d', password):
        return "VALID_PWD_NOT_INC_NUMBER_ERR"

    # 4. 특수문자 반드시 포함
    if settings.USER_PASSWORD_INCLUDE_SIMBOL and not re.search(r'[!@#$%^&*()_+{}|:"<>?`\-=[\];\',./]', password):
        return "VALID_PWD_NOT_INC_SIMBOL_ERR"

    # 모든 조건 통과
    return "VALID_PWD_SUCC"



