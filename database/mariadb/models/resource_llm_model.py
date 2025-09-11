from sqlalchemy import Column, Boolean, String, text
from sqlalchemy.dialects.mysql import INTEGER
from database.mariadb.models import Base, TimestampModel


class ResourceLLM(Base, TimestampModel):
    __tablename__ = "resource_llm"

    code = Column(
        String(255), primary_key=True, comment="LLM 코드 (ex: LLM-GEMINI, LLM-CHATGPT)"
    )
    name = Column(String(20), nullable=False, comment="LLM 이름")
    is_active = Column(Boolean, server_default=text("0"), comment="활성화 여부")
    priority = Column(INTEGER(display_width=11), nullable=False, comment="우선순위")
