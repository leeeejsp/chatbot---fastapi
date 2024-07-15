import fastapi
from db_config import connection
from pydantic import BaseModel
from chatbot import send_message_llm
from chatbot import updateStatus
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import sys
from fastapi.middleware.cors import CORSMiddleware


# 전역 예외 핸들러 설정
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    print('서버시작')
    updateStatus()
    scheduler.start()
    yield 
    logger.info('스케줄러 종료 중...')
    try:
        scheduler.shutdown(wait=False)  # 강제로 스케줄러 종료
    except Exception as e:
        logger.exception("Exception during scheduler shutdown: %s", e)
    logger.info('서버 종료')

# 30분 마다 업데이트
scheduler.add_job(updateStatus,"interval",minutes = 30)

app = fastapi.FastAPI(lifespan=lifespan)

class Message(BaseModel):
    message: str


# CORS에러 해결
origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # cross-origin request에서 cookie를 포함할 것인지 (default=False)
    allow_methods=["*"],     # cross-origin request에서 허용할 method들을 나타냄. (default=['GET']
    allow_headers=["*"],     # cross-origin request에서 허용할 HTTP Header 목록
)

@app.get("/")
async def start():
    return {"Hello":"chat_bot_server"}

@app.post('/api/main_chat')
async def main_chatbot(message: Message):
    response = send_message_llm(message.message)
    return {"response": response}

@app.post('/api/store_chat/{store_no}')
async def store_chatbot(store_no: int, message: Message):
    mes = str(store_no) + "번 가게에 대해 설명해줘. " + message.message
    response = send_message_llm(mes)
    return {"response": response}