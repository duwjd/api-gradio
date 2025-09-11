from sqlalchemy import Boolean, Column, String, Text, text
from sqlalchemy.dialects.mysql import INTEGER

from database.mariadb.models import Base, TimestampModel


class ResourceAiModel(Base, TimestampModel):
    __tablename__ = "resource_ai_model"

    code = Column(
        String(255), primary_key=True, comment="AI 모델 코드 (ex: AI-MODEL-000001)"
    )
    name = Column(String(255), nullable=True, comment="AI 모델 이름")
    sqs_queue_name = Column(String(255), nullable=True, comment="sqs 큐 배열")
    is_active = Column(Boolean, server_default=text("0"), comment="활성화 여부")
