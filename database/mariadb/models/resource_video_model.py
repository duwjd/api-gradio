from sqlalchemy import Column, SmallInteger, String

from database.mariadb.models import Base, TimestampModel


class ResourceVideoModel(Base, TimestampModel):
    __tablename__ = "resource_video_model"
    type = Column(
        String(255),
        primary_key=True,
        comment="모델 타입 (API, ENGINE)",
    )
    name = Column(
        String(255),
        comment="모델 이름",
    )
    order = Column(SmallInteger, comment="순서")
