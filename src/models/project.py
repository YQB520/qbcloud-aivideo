from datetime import datetime
from src.database import Base
from sqlalchemy import Column, CHAR, String, TIMESTAMP, JSON, select, SmallInteger, update
from sqlalchemy.orm import Session


class Project(Base):
    __tablename__ = "projects"

    id = Column(CHAR(36), primary_key=True, autoincrement=False)

    uid = Column(String(100), nullable=True)

    # 0--合成中  1--合成成功  2--合成失败
    status = Column(SmallInteger, default=0)

    file_name = Column(String(100), nullable=True)

    setting = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, nullable=True)

    updated_at = Column(TIMESTAMP, nullable=True)


class DBProject:
    def __init__(self, session: Session):
        self.session = session

    def first(self, _id: str):
        stmt = select(Project).where(Project.id == _id)
        return self.session.scalars(stmt).one_or_none()

    def create(self, _id: str, _setting: dict):
        is_exists = self.first(_id)
        if is_exists is None:
            now_time = datetime.now()
            patrick = Project(id=_id, uid=_setting["user_id"], setting=_setting,
                              created_at=now_time, updated_at=now_time)
            self.session.add(patrick)
            self.session.commit()

    def update(self, _id: str, _status: int, _file_name: str | None = None):
        is_exists = self.first(_id)
        if is_exists is not None:
            stmt = (
                update(Project)
                .where(Project.id == _id)
                .values(status=_status, file_name=_file_name)
            )
            self.session.execute(stmt)
            self.session.commit()
