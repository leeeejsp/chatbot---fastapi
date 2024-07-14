from db_config import connection
import json

FIND_ALL_STORE = 'SELECT * FROM STORE'

def get_menu_by_storeno(storeno):
    return 'SELECT * FROM MENU FROM STORE_STORENO = ' + str(storeno)

def get_store_by_storeno(storeno):
    return 'SELECT * FROM STORE = ' + str(storeno)


query = """
    select
        s.storeno,
        s.storename,
        s.latitude,
        s.longitude,
        s.address,
        nvl(s.introduce,' ') as introduce,
        s.operatingdate,
        s.operatinghours,
        s.totalreview,
        s.totalrating,
        s.likes,
        'http://localhost/store/' || to_char(s.storeno) as url,
        nvl(m.menuname,'아직 등록된 메뉴가 없습니다.') as menuname,
        nvl(to_char(m.price),'아직 등록된 메뉴가 없습니다.') as price
    from store s
    left join menu m
    on s.storeno = m.store_storeno
    """

cursor = connection.cursor()
cursor.execute(query)
rows = cursor.fetchall()

# 컬럼 이름 가져오기
columns = [col[0] for col in cursor.description]

columns_index = {}
for index, col in enumerate(cursor.description):
    columns_index[col[0]] = index

# 결과 구조화
stores_dict = {}
for row in rows:
    storeno, storename, latitude, longitude, address, introduce, operatingdate, operatinghours, totalreview, totalrating, likes, url, menuname, price = row
    if storeno not in stores_dict:
        stores_dict[storeno] = {
            '가게 번호': storeno,
            '가게 이름': storename,
            '위도': latitude,
            '경도': longitude,
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

# print(stores_dict)
# 딕셔너리를 리스트로 변환
stores_list = list(stores_dict.values())

# JSON 형식으로 변환
stores_json = json.dumps(stores_list, ensure_ascii=False, indent=4)

# JSON 출력
print(stores_json)

# 커서와 연결 종료
cursor.close()
connection.close()