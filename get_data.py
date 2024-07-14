from db_config import connection
import pandas as pd
import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import load_tools
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# 오라클 클라우드에 쿼리
def get_data(query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # 컬럼 이름 가져오기
    columns = [col[0] for col in cursor.description]

    # Row 객체를 딕셔너리로 변환
    stores = [dict(zip(columns, row)) for row in rows]

    # DB에서 가져온 데이터 전처리
    return get_dataframe_from_store(stores)

# 데이터 전처리 메소드
def get_dataframe_from_store(stores):
    df = pd.DataFrame(stores)

    # 남기고 싶은 컬럼들 리스트
    columns_to_keep = [
        'STORENO', 'STORENAME', 'LATITUDE', 'LONGITUDE', 'ADDRESS', 'INTRODUCE',
        'OPERATINGDATE', 'OPERATINGHOURS', 'TOTALREVIEW', 'TOTALRATING', 'LIKES'
    ]

    # 새로운 데이터프레임 생성
    df_filtered = df[columns_to_keep]

    # URL 컬럼 추가 : AI답변에 가게 상세페이지 유도하기 위함
    df_filtered['URL'] = df_filtered['STORENO'].apply(lambda x : 'http://localhost/store/' + str(x))

    # INTRODUCE컬럼이 None일 경우 공백처리
    df_filtered['INTRODUCE'] = df_filtered['INTRODUCE'].fillna('')

    # 남기는 컬럼들 한국어로 변환
    columns_to_koran = [
        '가게번호', '가게명', '위도', '경도', '가게주소', '가게 소개글',
        '운영일자', '운영시간', '총 리뷰 수', '리뷰 평점', '좋아요수', '가게 상세페이지 주소'
    ]
    df_filtered.columns = columns_to_koran

    return df_filtered

# 메인 챗봇 agent생성
def get_main_agent(df):

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    #tools = load_tools(['llm-math'], llm=llm)

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        # agent_type=AgentType.OPENAI_FUNCTIONS,
        # extra_tools=tools
    )

    return agent

stores = get_data("SELECT * FROM STORE").to_dict(orient='records')

# 스토어 정보를 문자열로 변환
store_details = "\n".join([
    f"가게번호: {store['가게번호']}, 가게명: {store['가게명']}, 위도: {store['위도']}, "
    f"경도: {store['경도']}, 가게주소: {store['가게주소']}, 가게 소개글: {store['가게 소개글']}, 운영일자: {store['운영일자']}, "
    f"운영시간: {store['운영시간']}, 총 리뷰 수: {store['총 리뷰 수']}, 리뷰 평점: {store['리뷰 평점']}, "
    f"좋아요수: {store['좋아요수']}, 가게 상세 페이지 주소: {store['가게 상세페이지 주소']}"
    for store in stores
])

# 프롬프트 템플릿 생성
prompt_template = """
너는 다양한 가게 정보들을 알고 있는 아주 친절하고 유능한 직원이야.
가게 정보는 아래와 같아. 가게를 추천해주는 경우에는 해당 가게의 상세페이지 주소도 같이 알려줘
그냥 추천해달라고 하는 경우 리뷰 수가 제일 높은 가게나 리뷰 평점이 제일 높은 가게나 좋아요수가 제일 높은 가게를 추천해주는데 마찬가지로 상세페이지 주소도 같이 알려줘

{store_details}
현재 시간은 13시45분이야
"""
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# 프롬프트 생성
prompt = prompt_template.format(store_details=store_details)

# 메시지 생성
messages1 = [
    (
        "system",
        prompt,
    ),
    ("human", "지금 몇 시야?"),
]
messages2 = [
    (
        "system",
        prompt,
    ),
    ("human", "방금한 질문이 뭐였지?"),
]

ai_msg1 = llm.invoke(messages1).content
ai_msg2 = llm.invoke(messages2).content

print("[[답변 1]]")
print(ai_msg1)
print('-'*50)

print("[[답변 2]]")
print(ai_msg2)
print('-'*50)

"""
[[질문 1]]
혜화동에 붕어빵가게 추천해줘

[[답변 1]]
혜화동에 붕어빵 가게라면 혜화붕어빵을 추천드려요! 

혜화붕어빵은 혜화동 명륜2가 28에 위치하고 있으며, 화요일부터 일요일까지 오후 3시 30분부터 밤 10시 30분까지 운영합니다. 

리뷰 평점은 4.0점으로 맛이 괜찮은 편이며, 총 1개의 리뷰가 있습니다. 

더 자세한 정보는  http://localhost/store/367 에서 확인하실 수 있습니다. 



[[질문 2]]
다른 먹을거 없나?

[[답변 2]]
네, 다른 먹거리 찾으시는군요! 어떤 종류의 음식을 좋아하세요? 혹시 드시고 싶은 메뉴가 있으신가요?

예를 들어,

* **매콤한 음식**이 땡긴다면, **먹깨비떡볶이 (http://localhost/store/380)**  혹은 **혜화역밀떡볶이 (http://localhost/store/379)** 를 추천드려요!
* **달콤한 간식**이 땡긴다면, **킹왕짱달고나 (http://localhost/store/383)**  혹은 **부산녹차씨앗호떡 (http://localhost/store/377)**  어떠세요?

원하시는 메뉴를 말씀해주시면 더 자세히 추천해드릴 수 있어요! 😊

"""