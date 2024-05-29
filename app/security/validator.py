import re
from app.config.settings import settings


def validate_usertype(usertype):
    # 유효한 회원 유형인지 확인
    if usertype in settings.USER_TYPE_ALLOW:
        return True, "USER_TYPE_SUCC"
    else:
        return False, "USER_TYPE_ERR"


def validate_nickname(nickname):
    # Korah 객체 생성
    # korah = Korah()
    #
    # # 한글 비속어 목록 가져오기
    # korean_bad_words = korah.get_bad_words('ko')
    #
    # # 영문 비속어 목록 가져오기
    # english_bad_words = korah.get_bad_words('en')
    #
    # # 모든 비속어를 한 리스트에 저장
    # all_bad_words = korean_bad_words + english_bad_words
    #
    # # 비속어 패턴 생성
    # bad_words_pattern = '|'.join(map(re.escape, all_bad_words))
    #
    # # 입력된 텍스트가 조건에 부합하는지 확인
    # if (
    #     re.match(r'^(?!.*(?:{})).*'.format(bad_words_pattern), nickname) and  # 비속어 입력 불가
    #     re.match(r'(?=.*[가-힣a-zA-Z]).*', nickname) and  # 한글이나 영문자 반드시 포함
    #     re.match(r'[가-힣a-zA-Z0-9]{2,20}$', nickname)  # 최소 2글자에서 최대 20글자 허용, 한글, 영문, 숫자 이외의 문자열 포함 불가
    # ):
    #     return True
    # else:
    #     return False
    return True, "VALID_NICK_SUCC"


def validate_password(password):
    # 5. 공백 입력 불가
    if settings.USER_PASSWORD_INCLUDE_SPACE and ' ' in password:
        return False, "VALID_PWD_INCLUDE_SPACE_ERR"

    # 1. 8자리 이상 최대 22자리
    if len(password) < settings.USER_PASSWORD_LENGTH_MIN or len(password) > settings.USER_PASSWORD_LENGTH_MAX:
        return False, "VALID_PWD_LENGTH_ERR"

    # 2. 대소문자 상관없이 문자열 반드시 포함
    if settings.USER_PASSWORD_INCLUDE_WORD and not re.search(r'[a-zA-Z]', password):
        return False, "VALID_PWD_NOT_INC_WORD_ERR"

    # 3. 숫자 반드시 포함
    if settings.USER_PASSWORD_INCLUDE_NUMBER and not re.search(r'\d', password):
        return False, "VALID_PWD_NOT_INC_NUMBER_ERR"

    # 4. 특수문자 반드시 포함
    if settings.USER_PASSWORD_INCLUDE_SIMBOL and not re.search(r'[!@#$%^&*()_+{}|:"<>?`\-=[\];\',./]', password):
        return False, "VALID_PWD_NOT_INC_SIMBOL_ERR"

    # 모든 조건 통과
    return True, "VALID_PWD_SUCC"


def validate_email(email):
    # 이메일 주소의 패턴을 정의
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # 이메일 주소 길이 검사
    if len(email) < settings.USER_EMAIL_LENGTH_MIN or len(email) > settings.USER_EMAIL_LENGTH_MAX:
        return False, "VALID_EMAIL_LENGTH_ERR"

    # 정규식을 사용하여 이메일 주소 유효성 검사
    if not re.match(pattern, email):
        return False, "VALID_EMAIL_PATTERN_ERR"

    # 모든 조건 통과
    return True, "VALID_EMAIL_SUCC"


