from db_config import connection
from langchain_google_genai import ChatGoogleGenerativeAI

# 오라클 클라우드에 쿼리
cursor = connection.cursor()
cursor.execute("SELECT * FROM STORE")
rows = cursor.fetchall()

# 컬럼 이름 가져오기
columns = [col[0] for col in cursor.description]

# Row 객체를 딕셔너리로 변환
stores = [dict(zip(columns, row)) for row in rows]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# 스토어 정보를 문자열로 변환
store_details = "\n".join([
    f"STORENO: {store['STORENO']}, STORENAME: {store['STORENAME']}, LATITUDE: {store['LATITUDE']}, "
    f"LONGITUDE: {store['LONGITUDE']}, ADDRESS: {store['ADDRESS']}, OPERATINGDATE: {store['OPERATINGDATE']}, "
    f"OPERATINGHOURS: {store['OPERATINGHOURS']}, TOTALREVIEW: {store['TOTALREVIEW']}, TOTALRATING: {store['TOTALRATING']}, "
    f"LIKES: {store['LIKES']}, CREATEDAT: {store['CREATEDAT']}, MODIFIEDAT: {store['MODIFIEDAT']}, "
    f"MEMBER_USERNAME: {store['MEMBER_USERNAME']}, PICTURE: {store['PICTURE']}"
    for store in stores
])

# 프롬프트 템플릿 생성
prompt_template = """
너는 다양한 가게 정보들을 알고 있는 아주 친절하고 유능한 직원이야.
가게 정보는 아래와 같아

{store_details}

"""

# 프롬프트 생성
prompt = prompt_template.format(store_details=store_details)

# 메시지 생성
messages = [
    (
        "system",
        prompt,
    ),
    ("human", "혜화동에 붕어빵가게 추천해줘"),
]

ai_msg = llm.invoke(messages)

print(ai_msg.content)

"""
ai 답변

혜화동에 붕어빵 가게는 혜화붕어빵이라는 곳이 있어요! 

혜화붕어빵은 서울 종로구 명륜2가 28에 위치하고 있으며, 화요일부터 일요일까지 오후 3시 30분부터 밤 10시 30분까지 운영합니다.

총 1개의 리뷰에서 4.0점의 평점을 받았고, 좋아요는 0개입니다.

더 궁금한 점이 있으신가요? 😊

"""