from app.config.variables import messages


def make_response(status: str, code: str, data: dict | list | None = None):
    response = {
        "status": messages[status],
        "code": code,
        "message": messages[code]
    }
    if data:
        response["data"] = data

    return response


def make_nickname_sample(nickname: str):
    unique_life_words = [
        "고양이", "장미", "사자", "참새", "소나무", "대왕고래", "바나나", "코끼리", "다람쥐", "해바라기",
        "강아지", "벚꽃", "호랑이", "비둘기", "은행나무", "돌고래", "포도", "기린", "햄스터", "무궁화",
        "늑대", "연꽃", "표범", "갈매기", "단풍나무", "상어", "오렌지", "코알라", "토끼", "튤립",
        "고릴라", "알로에", "캥거루", "매화", "악어", "수국", "기러기", "백합", "양귀비", "대나무",
        "백조", "라일락", "부엉이", "파인애플", "라쿤", "모란", "부추", "복숭아", "자두", "사슴",
        "장수풍뎅이", "메뚜기", "코코넛", "망고", "낙타", "수달", "박쥐", "해삼", "산호", "오징어",
        "문어", "성게", "소", "양", "염소", "돼지", "닭", "거북이", "앵무새", "펭귄",
        "비버", "가재", "바퀴벌레", "노루", "칠면조", "홍학", "타조", "두루미", "스컹크", "오소리",
        "호랑나비", "나비", "나방", "잠자리", "반딧불이", "개미", "벌", "무당벌레", "진딧물", "사마귀",
        "카멜레온", "이구아나", "두꺼비", "개구리", "청개구리", "맹꽁이", "해파리", "말미잘", "불가사리", "조개",
        "가리비", "대합", "굴", "새우", "게", "랍스터", "멸치", "정어리", "고등어", "참치",
        "연어", "송어", "잉어", "메기", "황소개구리", "피라냐", "금붕어", "자라", "잉어", "가물치",
        "뱀장어", "무지개송어", "담배", "당근", "양파", "마늘", "파슬리", "로즈마리", "타임", "세이지",
        "바질", "박하", "딸기", "블루베리", "라즈베리", "블랙베리", "크랜베리", "체리", "복분자", "앵두",
        "월귤", "보리", "밀", "쌀", "옥수수", "보리", "호밀", "귀리", "수수", "메밀",
        "보리수", "구아바", "파파야", "용과", "참외", "수박", "멜론", "아보카도", "레몬", "라임",
        "귤", "유자", "자몽", "올리브", "커피나무", "차나무", "호두나무", "밤나무", "도토리나무", "뽕나무",
        "매실나무", "복숭아나무", "배나무", "사과나무", "무화과나무", "감나무", "밤나무", "대추나무", "체리나무", "아몬드나무",
        "피스타치오나무", "카카오나무", "바나나나무", "파파야나무", "코코야자나무", "호박", "단호박", "무", "순무", "배추",
        "양배추", "브로콜리", "콜리플라워", "케일", "비트", "근대", "시금치", "상추", "쑥갓", "열무",
        "얼갈이배추", "적채", "청경채", "고추", "파프리카", "피망", "토마토", "방울토마토", "가지", "오이",
        "호박", "애호박", "죽순", "여주", "오크라", "셀러리", "브로콜리", "아스파라거스", "아티초크", "루꼴라",
        "석죽", "선인장", "세쿼이아", "소나무", "소철", "소프라노", "수국", "수선화", "수양버들", "스트로브잣나무",
        "식나무", "식죽나무", "아도니스", "아데니움", "아로니아", "아스파라거스", "아카시아", "안개나무", "안스리움", "알로카시아",
        "알로에", "알팔파", "애기풀", "야광나무", "야자나무", "양귀비", "양송이버섯", "어성초", "에버그린", "에키네시아",
        "연꽃", "영산홍", "영춘화", "예초기", "오랑캐꽃", "옥잠화", "왕벚나무", "용담", "용설란", "우산나무",
        "운모", "원추리", "월계수", "유카리나무", "율마", "으아리", "은단풍나무", "은행나무", "이끼", "이팝나무",
        "인동초", "일본목련", "일본잎갈나무", "자귀나무", "자란", "자바라", "장미", "장산나무", "장수풍뎅이", "잣나무",
        "장미", "재스민", "전나무", "정향나무", "조릿대", "주목", "죽백나무", "줄풀", "참나무", "참식나무",
        "창포", "천냥나무", "천리향", "천선과", "천엽", "천왕석", "철쭉", "초롱꽃", "초롱꽃나무", "초피나무",
        "추명목", "추위", "칡", "카네이션", "카네프리", "칸나", "캐스터빈", "케미칼나무", "켄타우레아", "코끼리",
        "코스모스", "콩나물", "콜로카시아", "쿠바", "쿠푸시우", "쿠카", "클로버", "키위", "타이페", "탱자나무",
        "텔레키아", "텔레크리움", "텔레타리움", "톨드", "톨스프레드", "튜립", "튜피", "튜피나", "튤립", "파파야",
        "파란병꽃나무", "파초", "팔레스타인무화과", "팜트리", "팜팜트리", "패랭이꽃", "팬지", "펜도라", "펜네로사", "포인세티아",
        "포플러", "프라기레나", "프레리이옥", "프리지아", "플라워", "플로우", "플루메리아", "피나무", "피라칸타", "피톤치드",
        "필레리움", "필리핀고무나무", "하이비스커스", "하치즈카", "한라산", "해국", "해금강", "해바라기", "해송", "해수",
        "행정사", "호랑가시나무", "호랑가시나무", "호두나무", "호박", "호야", "화단", "화분", "화산송이", "화초",
        "화초모종", "화초용", "화초장식", "화초화분", "화초효과", "화초효능", "화초향", "환삼덩굴", "황금사철나무", "황금알로카시아",
        "황금올리브나무", "황금잎꽃나무", "황기", "황칠나무", "회화나무", "후레쉬마카", "후쿠시아", "후박나무", "히어리", "히카마",
        "히크리", "히코스기", "히토기아", "히프노스", "히히쿰", "히토즈크", "히노키", "힐러", "힐러리움", "힐러스"
    ]

    return nickname + " sample"
