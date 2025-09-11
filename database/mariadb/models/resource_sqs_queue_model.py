from sqlalchemy import Boolean, Column, String, text

from database.mariadb.models import Base, TimestampModel


class ResourceSqsQueue(Base, TimestampModel):
    __tablename__ = "resource_sqs_queue"

    code = Column(
        String(255), primary_key=True, comment="분석 코드 (ex: AI-SQS-000001)"
    )

    env = Column(
        String(255),
        comment="운영 환경",
    )
    name = Column(String(255), nullable=True, comment="queue 이름")
    type = Column(String(255), nullable=False, comment="queue 타입")
    is_active = Column(Boolean, server_default=text("0"), comment="활성화 여부")
