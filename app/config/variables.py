from app.config.settings import settings


messages = dict()

# 공통
messages['EXCEPTION'] = "알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
messages['NO_PERMISSION'] = "권한이 없습니다."
messages['FILE_NOT_FOUND'] = "파일을 찾을 수 없습니다."
messages['FILE_STORE_FAIL'] = "파일 저장에 실패하였습니다."
messages['FILE_TYPE_ERR'] = "지원하지 않는 파일 형식입니다."

# access token 관련
messages['ACCESS_TOKEN_VERIFY'] = "토큰 검증에 성공하였습니다."
messages['ACCESS_TOKEN_FOUND'] = "토큰은 찾았습니다."
messages['ACCESS_TOKEN_EXPIRED'] = "토근이 만료되었습니다."
messages['ACCESS_TOKEN_INVALID'] = "유효하지 않은 토큰입니다."
messages['ACCESS_TOKEN_REQUIRE'] = "토큰은 필수 입력사항 입니다."

messages['USER_LOGIN_SUCC'] = "로그인에 성공하였습니다."
messages['USER_LOGIN_FAIL'] = "로그인에 실패하였습니다."
messages['USER_LOGIN_AUTH_FAIL'] = "사용자 인증 정보가 올바르지 않습니다."
messages['USER_LOGIN_EMAIL_REQUIRED'] = "이메일을 입력해주세요"
messages['USER_LOGIN_PASSWORD_REQUIRED'] = "비밀번호를 입력해주세요"
messages['USER_LOGIN_TYPE_REQUIRED'] = "타입을 입력해주세요"
messages['USER_LOGIN_AGREE_FAIL'] = "약관 동의, 개인정보 처리방침 동의, 만 14세 이상 동의가 필요합니다."

messages['USER_NOT_MATCH'] = "유저 정보가 일치하지 않습니다."
messages['USER_NOT_FOUND'] = "유저를 찾을 수 없습니다."
messages['USER_NOT_ADMIN'] = "관리자 권한이 없습니다."
# User Create, Read, Update, Delete, Login, User Check 관련
messages['USER_CREATE_SUCC'] = "회원가입이 완료되었습니다."
messages['USER_CREATE_FAIL'] = "회원가입에 실패하였습니다."
messages['USER_CREATE_REQUIRED_FIELDS'] = "필수 입력사항을 입력해주세요."
messages['USER_AGREE_PRIVACY_REQUIRED'] = "개인정보 처리방침에 동의해주세요."
messages['USER_AGREE_TERMS_REQUIRED'] = "이용 약관에 동의해주세요."
messages['USER_AGREE_MARKETING_REQUIRED'] = "마케팅 정보 수신에 동의해주세요."

messages['USER_TYPE_SUCC'] = "유효한 회원 유형입니다."
messages['USER_TYPE_ERR'] = "유효하지 않은 회원 유형입니다."

messages['USER_READ_SUCC'] = "회원 정보 조회에 성공하였습니다."
messages['USER_READ_FAIL'] = "회원 정보 조회에 실패하였습니다."

messages['USER_BLOCKED'] = "사용이 제한된 계정입니다."

messages['NICKNAME_DOES_NOT_EXIST'] = "사용 가능한 닉네임입니다."
messages['NICKNAME_ALREADY_EXIST'] = "이미 존재하는 닉네임입니다."

messages['EMAIL_DOES_NOT_EXIST'] = "사용 가능한 이메일 주소입니다."
messages['EMAIL_ALREADY_EXIST'] = "이미 존재하는 이메일 주소입니다."

messages['USER_UPDATE_SUCC'] = "회원 정보 수정에 성공하였습니다."
messages['USER_UPDATE_FAIL'] = "회원 정보 수정에 실패하였습니다."
messages['USER_UPDATE_NICKNAME_SUCC'] = "닉네임 업데이트에 성공했습니다."
messages['USER_UPDATE_NICKNAME_FAIL'] = "닉네임 업데이트에 실패했습니다."
messages['USER_UPDATE_NICKNAME_NOT_FOUND'] = "닉네임을 입력해 주세요."
messages['USER_UPDATE_PROFILE_SUCC'] = "프로필 업데이트에 성공했습니다."
messages['USER_UPDATE_PROFILE_FAIL'] = "프로필 업데이트에 실패했습니다."
messages['USER_UPDATE_PROFILE_NOT_FOUND'] = "프로필을 찾을 수 없습니다."
messages['USER_UPDATE_PROFILE_IMAGE_SUCC'] = "프로필 이미지 업데이트에 성공했습니다."
messages['USER_UPDATE_PROFILE_IMAGE_FAIL'] = "프로필 이미지 업데이트에 실패했습니다."
messages['USER_UPDATE_PROFILE_IMAGE_NOT_FOUND'] = "프로필 이미지를 찾을 수 없습니다."
messages['USER_UPDATE_PASSWORD_SUCC'] = "비밀번호 업데이트에 성공했습니다."
messages['USER_UPDATE_PASSWORD_FAIL'] = "비밀번호 업데이트에 실패했습니다."
messages['USER_UPDATE_PASSWORD_NOT_FOUND'] = "비밀번호를 입력해 주세요."
messages['USER_UPDATE_ISAGREE_SUCC'] = "광고수신 동의 업데이트에 성공했습니다."
messages['USER_UPDATE_ISAGREE_FAIL'] = "광고수신 동의 업데이트에 실패했습니다."

messages['USER_DELETE_SUCC'] = "회원 탈퇴에 성공하였습니다."
messages['USER_DELETE_FAIL'] = "회원 탈퇴에 실패하였습니다."

messages['VALID_NICK_SUCC'] = "유효한 닉네임입니다."
messages['VALID_NICK_REQUIRE_ERR'] = "닉네임은 필수 입력사항 입니다."

messages['VALID_EMAIL_SUCC'] = "유효한 이메일 주소입니다."
messages['VALID_EMAIL_REQUIRE_ERR'] = "이메일은 필수 입력사항 입니다."
messages['VALID_EMAIL_LENGTH_ERR'] = "이메일 주소는 {}자리 이상 {}자리 이하여야 합니다.".format(
    settings.USER_EMAIL_LENGTH_MIN,
    settings.USER_EMAIL_LENGTH_MAX
)
messages['VALID_EMAIL_PATTERN_ERR'] = "유효하지 않은 이메일 주소입니다."

messages['VALID_PWD_SUCC'] = "유효한 비밀번호입니다."
messages['VALID_PWD_REQUIRE_ERR'] = "비밀번호는 필수 입력사항 입니다."
messages['VALID_PWD_INCLUDE_SPACE_ERR'] = "비밀번호에 공백을 포함할 수 없습니다."
messages['VALID_PWD_LENGTH_ERR'] = "비밀번호는 {}자리 이상 {}자리 이하여야 합니다.".format(
    settings.USER_PASSWORD_LENGTH_MIN,
    settings.USER_PASSWORD_LENGTH_MAX
)
messages['VALID_PWD_NOT_INC_WORD_ERR'] = "비밀번호는 반드시 문자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_NUMBER_ERR'] = "비밀번호는 반드시 숫자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_SIMBOL_ERR'] = "비밀번호는 반드시 특수문자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_UPPER_ERR'] = "비밀번호는 반드시 대문자를 포함해야 합니다."
messages['VALID_PWD_NOT_INC_LOWER_ERR'] = "비밀번호는 반드시 소문자를 포함해야 합니다."

# Video Create, Read, Update, Delete 관련
messages['INVALID_PARAM_PAGE'] = "유효하지 않은 페이지 번호입니다."
messages['INVALID_PARAM_PAGE_SIZE'] = "유효하지 않은 페이지 크기입니다."
messages['INVALID_PARAM_KEYWORD'] = "유효하지 않은 검색어입니다."
messages['INVALID_PARAM_TYPE'] = "유효하지 않은 타입입니다."
messages['INVALID_PARAM_ORDER_BY'] = "유효하지 않은 정렬 조건입니다."

messages['VIDEO_NOT_FOUND'] = "비디오를 찾을 수 없습니다."

messages['VIDEO_CREATE_SUCC'] = "컨텐츠 생성에 성공하였습니다."
messages['VIDEO_CREATE_FAIL'] = "컨텐츠 생성에 실패하였습니다."

messages['VIDEO_SEARCH_SUCC'] = "컨텐츠 검색에 성공하였습니다."
messages['VIDEO_READ_SUCC'] = "컨텐츠 조회에 성공하였습니다."
messages['VIDEO_READ_FAIL'] = "컨텐츠 조회에 실패하였습니다."

messages['VIDEO_UPDATE_SUCC'] = "컨텐츠 수정에 성공하였습니다."
messages['VIDEO_UPDATE_FAIL'] = "컨텐츠 수정에 실패하였습니다."

messages['VIDEO_DELETE_SUCC'] = "컨텐츠가 삭제되었습니다."
messages['VIDEO_DELETE_FAIL'] = "컨텐츠 삭제에 실패하였습니다."

messages['VIDEO_VIEW_INSERT_SUCC'] = "컨텐츠 조회수를 갱신하였습니다."

messages['REVIEW_READ_LIST_SUCC'] = "리뷰 조회에 성공하였습니다."
messages['REVIEW_CREATE_SUCC'] = "리뷰 등록에 성공했습니다."
messages['REVIEW_READ_SUCC'] = "리뷰 조회에 성공했습니다."
messages['REVIEW_UPDATE_SUCC'] = "리뷰 수정에 성공했습니다."
messages['REVIEW_UPDATE_FAIL'] = "리뷰 수정에 실패했습니다."
messages['REVIEW_UPDATE_PERMISSION_ERR'] = "리뷰 수정 권한이 없습니다."
messages['REVIEW_DELETE_SUCC'] = "리뷰 삭제에 성공했습니다."
messages['REVIEW_DELETE_FAIL'] = "리뷰 삭제에 실패했습니다."
messages['REVIEW_DELETE_PERMISSION_ERR'] = "리뷰 삭제 권한이 없습니다."
