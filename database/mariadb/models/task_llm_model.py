from sqlalchemy import Column, Double, Integer, SmallInteger, String, Text, text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from database.mariadb.models import Base, TimestampModel


class TaskLLM(Base, TimestampModel):
    __tablename__ = "task_llm"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="유저 ID")
    project_id = Column(Integer, nullable=False, comment="프로젝트 ID")  # 프로젝트 ID
    analysis_type = Column(
        String(255),
        nullable=False,
        comment="분석 타입 (ex: analysis | llm | assist | crawl)",
    )
    analysis_code = Column(String(255), nullable=False)
    llm_code = Column(
        String(255), nullable=True, comment="LLM 코드 (ex: LLM-GEMINI, LLM-CHATGPT)"
    )
    status = Column(
        String(255), nullable=False
    )  # Enum 사용시 변경 사항 적용 안됨 나중에 변경 예정
    progress = Column(
        SmallInteger, server_default=text("0"), comment="진행율"
    )  # 진행도 표시 (0~100)
    process = Column(
        String(255), nullable=True, comment="분석 프로세스"
    )  # llm | document_parser | frame-pack

    request_body = Column(MEDIUMTEXT, nullable=True, comment="분석 request body")
    result = Column(Text, nullable=True, comment="분석 결과")  # 결과 JSON 저장
    llm_result = Column(MEDIUMTEXT, nullable=True, comment="llm 결과")
    prompt = Column(Text, nullable=True, comment="프롬프트")
    error_code = Column(String(255), nullable=True, comment="에러 코드")
    error_message = Column(Text, nullable=True, comment="에러 메세지")
    llm_end_at = Column(Double, nullable=True, comment="llm 종료 시간(초)")
    end_at = Column(Double, nullable=True, comment="종료 시간(초)")
    empty_tag = Column(
        Text, server_default=text("'[]'"), comment="llm 결과 빈 태그 목록"
    )
