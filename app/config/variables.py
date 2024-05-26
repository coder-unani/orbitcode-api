from app.config.settings import settings


messages = dict()

# 공통
messages[True] = "success"
messages[False] = "fail"
messages['EXCEPTION'] = "알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
messages['FILE_NOT_FOUND'] = "파일을 찾을 수 없습니다."
messages['FILE_STORE_FAIL'] = "파일 저장에 실패하였습니다."
messages['FILE_TYPE_ERR'] = "지원하지 않는 파일 형식입니다."

# access token 관련
messages['ACCESS_TOKEN_FOUND'] = "토큰은 찾았습니다."
messages['ACCESS_TOKEN_EXPIRED'] = "토근이 만료되었습니다."
messages['ACCESS_TOKEN_INVALID'] = "유효하지 않은 토큰입니다."
messages['ACCESS_TOKEN_REQUIRE'] = "토큰은 필수 입력사항 입니다."

# User Create, Read, Update, Delete, Login, User Check 관련
messages['USER_CREATE_SUCC'] = "회원가입이 완료되었습니다."
messages['USER_CREATE_FAIL'] = "회원가입에 실패하였습니다."

messages['USER_TYPE_SUCC'] = "유효한 회원 유형입니다."
messages['USER_TYPE_ERR'] = "유효하지 않은 회원 유형입니다."

messages['USER_VERIFY_SUCC'] = "로그인에 성공하였습니다."
messages['USER_VERIFY_FAIL'] = "로그인에 실패하였습니다."
messages['USER_READ_SUCC'] = "회원 정보 조회에 성공하였습니다."

messages['NICKNAME_DOES_NOT_EXIST'] = "사용 가능한 닉네임입니다."
messages['NICKNAME_ALREADY_EXIST'] = "이미 존재하는 닉네임입니다."

messages['EMAIL_DOES_NOT_EXIST'] = "사용 가능한 이메일 주소입니다."
messages['EMAIL_ALREADY_EXIST'] = "이미 존재하는 이메일 주소입니다."

messages['USER_UPDATE_PROFILE_IMAGE_SUCC'] = "사용자의 프로필 이미지 업데이트에 성공했습니다."
messages['USER_UPDATE_PROFILE_IMAGE_FAIL'] = "사용자의 프로필 이미지 업데이트에 실패했습니다."

messages['VALID_EMAIL_SUCC'] = "유효한 이메일 주소입니다."
messages['VALID_EMAIL_REQUIRE_ERR'] = "이메일은 필수 입력사항 입니다."
messages['VALID_EMAIL_LENGTH_ERR'] = "이메일 주소는 {}자리 이상 {}자리 이하여야 합니다.".format(settings.USER_EMAIL_LENGTH_MIN, settings.USER_EMAIL_LENGTH_MAX)
messages['VALID_EMAIL_PATTERN_ERR'] = "유효하지 않은 이메일 주소입니다."

messages['VALID_PWD_SUCC'] = "유효한 비밀번호입니다."
messages['VALID_PWD_REQUIRE_ERR'] = "비밀번호는 필수 입력사항 입니다."
messages['VALID_PWD_INCLUDE_SPACE_ERR'] = "비밀번호에 공백을 포함할 수 없습니다."
messages['VALID_PWD_LENGTH_ERR'] = "비밀번호는 {}자리 이상 {}자리 이하여야 합니다.".format(settings.USER_PASSWORD_LENGTH_MIN, settings.USER_PASSWORD_LENGTH_MAX)
messages['VALID_PWD_NOT_INC_WORD_ERR'] = "비밀번호는 반드시 문자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_NUMBER_ERR'] = "비밀번호는 반드시 숫자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_SIMBOL_ERR'] = "비밀번호는 반드시 특수문자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_UPPER_ERR'] = "비밀번호는 반드시 대문자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_LOWER_ERR'] = "비밀번호는 반드시 소문자를 포함해야 합니다."

messages['VALID_NICK_SUCC'] = "유효한 닉네임입니다."
messages['VALID_NICK_REQUIRE_ERR'] = "닉네임은 필수 입력사항 입니다."

# Video Create, Read, Update, Delete 관련
messages['VIDEO_CREATE_SUCC'] = "동영상이 성공적으로 생성되었습니다."
messages['VIDEO_CREATE_FAIL'] = "동영상 생성에 실패하였습니다."

messages['VIDEO_READ_SUCC'] = "동영상 조회에 성공하였습니다."
messages['VIDEO_READ_FAIL'] = "동영상 조회에 실패하였습니다."

messages['VIDEO_UPDATE_SUCC'] = "동영상이 성공적으로 수정되었습니다."
messages['VIDEO_UPDATE_FAIL'] = "동영상 수정에 실패하였습니다."

messages['VIDEO_DELETE_SUCC'] = "동영상이 성공적으로 삭제되었습니다."
messages['VIDEO_DELETE_FAIL'] = "동영상 삭제에 실패하였습니다."


