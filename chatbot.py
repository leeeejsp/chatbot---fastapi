from db_config import connection
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
from collections import deque
import config
import cx_Oracle

llm=None
prompt=None
stores_json=None
history_queue=None


"""
DB로부터 가게 정보와 해당 가게의 메뉴정보를 dict형태로 가져온다.
"""
def get_data():
    global stores_json

    # Oracle Database 연결 정보
    connection = cx_Oracle.connect(user=config.DB_USER, 
                                password=config.DB_PASSWORD, 
                                dsn=config.DB_DSN)
    
    # 쿼리
    query = """
        select
            s.storeno,
            s.storename,
            s.address,
            nvl(s.introduce,' ') as introduce,
            s.operatingdate,
            s.operatinghours,
            s.totalreview,
            s.totalrating,
            s.likes,
            'http://localhost:8080/store/' || to_char(s.storeno) as url,
            nvl(m.menuname,' ') as menuname,
            nvl(to_char(m.price),' ') as price
        from store s
        left join menu m
        on s.storeno = m.store_storeno
        """

    # DB에서 데이터 가져오기
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    # 결과 구조화
    stores_dict = {}
    for row in rows:
        storeno, storename, address, introduce, operatingdate, operatinghours, totalreview, totalrating, likes, url, menuname, price = row
        if storeno not in stores_dict:
            stores_dict[storeno] = {
                '가게 번호': storeno,
                '가게 이름': storename,
                '주소': address,
                '가게 소개 글': introduce,
                '운영일자': operatingdate,
                '운영시간': operatinghours,
                '총 리뷰 수': totalreview,
                '리뷰 평점': totalrating,
                '좋아요 수': likes,
                '가게 상세 페이지 주소': url,
                '메뉴': []
            }
        stores_dict[storeno]['메뉴'].append({
            '메뉴 이름': menuname,
            '메뉴 가격': price
        })

    # 딕셔너리를 리스트로 변환
    stores_list = list(stores_dict.values())

    # JSON 형식으로 변환
    stores_json = json.dumps(stores_list, ensure_ascii=False)

    # 커서와 연결 종료
    cursor.close()
    connection.close()

    return stores_json

'''
AI모델을 가져온다.
'''
def get_llm():
    global llm
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",temperature=0)
    return llm

'''
AI에 학습시킬 내용을 가져온다.
'''
def get_prompt(stores_json):
    global prompt

    # 프롬프트 템플릿 생성
    prompt = """
    너는 다양한 가게 정보들을 알고 있는 아주 친절하고 유능한 직원이야.
    가게 정보는 아래와 같아. 가게를 추천해주는 경우에는 해당 가게의 상세페이지 주소도 같이 알려주고 메뉴 1개 정도만 알려줘
    음식 종류를 말하지 않고 추천해달라고 하는 경우 리뷰 수가 많은 가게나 리뷰 평점이 높은 가게나 좋아요수가 제일 높은 가게를 추천해주는데 대략 3곳을 추천해주는데 해당하는 가게의 메뉴가 어떤 맛인지도 간략하게 표현해줘. 마찬가지로 상세페이지 주소도 같이 알려줘
    만약에 아래에 있는 가게 정보에 없는 것을 물어보는 경우에는 해당하는 가게는 없다고 알려주고 다른 가게를 추천해줘
    앞으로 알려줄때는 가게 번호에 대한 정보는 빼고 설명해줘
    그리고 운영시간은 시작시간과 끝나는 시간이 '-'기호로 구분돼있고, 운영일자에 해당하는 내용은 가게를 여는 요일이 ,를 기준으로 구분돼있어 
    만약에 현재 운영중인 가게에 대해 물어보는 경우 현재시간이 운영시간과 운영일자 안에 포함돼있는 가게만 알려주고 전부 포함돼있지 않은 경우 문을 연 가게가 없다고 알려줘 
    그리고 '네, 현재 시간과 요일을 알려주셔서 감사합니다.'라는 말 하지 말아줘
    
    """ + stores_json
   
    return prompt

'''
물어본것에 대해 응답을 받는 메소드
'''
def get_response_from_llm(llm, prompt, send_message):
    global history_queue
    if history_queue is None:
        history_queue = deque()

    # 메시지 생성
    message = [
        (
            "system",
            prompt + str(history_queue),
        ),
        (
            "human",
            send_message # 사용자가 보내는 내용
        ),
    ]

    # 답변
    response_message = llm.invoke(message).content

    # 이전 질문 체이닝
    if len(history_queue) >= 5:
        history_queue.popleft()
    history = {
        '이전 질문':send_message,
        '답변': response_message
    }
    history_queue.append(history)

    return response_message
    

'''
메소드로 분리한 과정들을 하나로 통합
'''
weekday = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
def send_message_llm(send_message):
    global llm, prompt, stores_json

    # 현재 시간 정보 추가
    now = datetime.now()
    send_message += " 현재 시간은 " + now.strftime('%Y-%m-%d %H:%M:%S') + "이며, 오늘은 " + weekday[now.weekday()] + "요일"

    if stores_json is None or prompt is None or llm is None:
        stores_json = get_data()
        prompt = get_prompt(stores_json)
        llm = get_llm()

    response = get_response_from_llm(llm, prompt, send_message)
    return response

# DB에 데이터 추가 및 수정 사항에 대비하여 갱신하는 메소드
def updateStatus():
    global llm, prompt, stores_json

    stores_json = get_data()
    prompt = get_prompt(stores_json)
    llm = get_llm()
    print('상태 업데이트 완료')