from sqlalchemy import Boolean, Column, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER

from database.mariadb.models import Base, TimestampModel


class ResourceWorker(Base, TimestampModel):
    __tablename__ = "resource_worker"

    code = Column(
        String(255), primary_key=True, comment="worker 코드 (ex: AI-WORKER-000001)"
    )
    name = Column(String(255), nullable=True, comment="worker 이름")
    type = Column(
        String(255), nullable=False, comment="worker 타입 api | master | worker"
    )
    host = Column(String(255), nullable=False, comment="worker host")
    port = Column(String(255), nullable=False, comment="worker port")
    is_active = Column(Boolean, server_default=text("0"), comment="활성화 여부")
