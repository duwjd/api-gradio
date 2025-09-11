from sqlalchemy import Column, Double, Integer, SmallInteger, String, Text, text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from database.mariadb.models import Base, TimestampModel


class TaskEngine(Base, TimestampModel):
    __tablename__ = "task_engine"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="유저 ID")
    project_id = Column(Integer, nullable=False, comment="프로젝트 ID")  # 프로젝트 ID
    analysis_code = Column(String(255), nullable=False)
    status = Column(
        String(255), nullable=False
    )  # Enum 사용시 변경 사항 적용 안됨 추후에 변경 필요
    progress = Column(
        SmallInteger, server_default=text("0"), comment="진행율"
    )  # 진행도 표시 (0~100)
    process = Column(
        String(255), nullable=False, comment="분석 프로세스"
    )  # llm | document_parser | frame-pack
    order_no = Column(SmallInteger, nullable=True, comment="순서")
    result = Column(Text, nullable=True, comment="분석 결과")  # 결과 JSON 저장
    error_code = Column(SmallInteger, nullable=True, comment="에러 코드")
    error_message = Column(Text, nullable=True, comment="에러 메세지")
    end_at = Column(Double, nullable=True, comment="종료 시간(초)")
