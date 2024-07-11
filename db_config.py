import cx_Oracle
import config

cx_Oracle.init_oracle_client(lib_dir=config.DB_CLINET_LOCATION) 

# Oracle Database 연결 정보
connection = cx_Oracle.connect(user=config.DB_USER, 
                               password=config.DB_PASSWORD, 
                               dsn=config.DB_DSN)
