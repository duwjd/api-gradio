from sqlalchemy import Column, String, Text

from database.mariadb.models import Base, TimestampModel


class ResourceRefImage(Base, TimestampModel):
    __tablename__ = "resource_ref_image"
    code = Column(
        String(255),
        primary_key=True,
        comment="레퍼런스 이미지 코드 (ex: AI-REF-IMAGE-000001)",
    )
    type = Column(String(255), nullable=True, comment="레퍼런스 이미지 타입")
    option = Column(Text, nullable=True, comment="옵션 json")
    image_url = Column(Text, nullable=True, comment="이미지 url")
    mask_url = Column(Text, nullable=True, comment="마스크 url")
