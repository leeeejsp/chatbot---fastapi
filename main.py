import fastapi
from db_config import connection

app = fastapi.FastAPI()

@app.get('/')
def home():
    return {"message":"hello world!"}


@app.get('/store')
def get_store():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM STORE")
    rows = cursor.fetchall()
    
    # 컬럼 이름 가져오기
    columns = [col[0] for col in cursor.description]

    # Row 객체를 딕셔너리로 변환
    stores = [dict(zip(columns, row)) for row in rows]

    return {"stores": stores}