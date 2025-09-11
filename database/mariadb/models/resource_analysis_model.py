from sqlalchemy import Boolean, Column, String, text

from database.mariadb.models import Base, TimestampModel


class ResourceAnalysis(Base, TimestampModel):
    __tablename__ = "resource_analysis"

    code = Column(
        String(255), primary_key=True, comment="분석 코드 (ex: AI-ANALYSIS-000001)"
    )

    group = Column(
        "group",
        String(255),
        server_default=text("'[]'"),
        comment='그룹 ["10k1m.com"], [] 빈 배열은 모든 그룹에 처리 가능',
    )
    name = Column(
        String(255), nullable=True, comment="분석 셋 이름 (ex: gemgem 문서 분석용)"
    )
    type = Column(String(255), nullable=False, comment="분석 타입(gg-project)")
    is_active = Column(Boolean, server_default=text("0"), comment="활성화 여부")
