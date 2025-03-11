from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

db_host = config('DB_HOST', default="localhost", cast=str)

db_port = config('DB_PORT', default="3306", cast=str)

db_database = config('DB_DATABASE', default="ai_agent", cast=str)

db_username = config('DB_USERNAME', default="ai_agent", cast=str)

db_password = config('DB_PASSWORD', default="123456", cast=str)

db_url = f"mysql+mysqlconnector://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"

debug = config('DEBUG', default=False, cast=bool)


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self):
        self.engine = None
        self.connection()

    def connection(self):
        self.engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # 自动检测连接有效性
            pool_recycle=3600,  # 每小时回收连接（避免 MySQL 8小时断开问题）
            echo=debug  # 显示SQL日志
        )

    def session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()
