from sqlalchemy import Boolean, Column, String, Text, text

from database.mariadb.models import Base, TimestampModel


class ResourcePrompt(Base, TimestampModel):
    __tablename__ = "resource_prompt"

    code = Column(
        String(255), primary_key=True, comment="프롬프트 코드 (ex: AI-PROMPT-000001)"
    )
    analysis_code = Column(
        String(255), nullable=True, comment="분석 코드 (ex: AI-PHOTO2VIDEO-000001)"
    )
    group = Column(String(255), nullable=True, comment='그룹 (ex: ["10k1m.com"])')
    name = Column(String(255), nullable=True, comment="프롬프트 이름")
    llm_code = Column(String(255), nullable=True, comment="LLM 코드 (ex: LLM-CHATGPT)")
    prompt = Column(Text, nullable=True, comment="프롬프트")
    is_active = Column(Boolean, server_default=text("1"), comment="활성 여부")
