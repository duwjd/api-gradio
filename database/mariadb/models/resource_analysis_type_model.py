from sqlalchemy import Column, String

from database.mariadb.models import Base, TimestampModel


class ResourceAnalysisType(Base, TimestampModel):
    __tablename__ = "resource_analysis_type"

    type = Column(
        String(255),
        primary_key=True,
        comment="분석 타입 (ex: analysis | type | assist | crawl)",
    )
    name = Column(
        String(255),
        nullable=True,
        comment="분석 타입 이름",
    )
