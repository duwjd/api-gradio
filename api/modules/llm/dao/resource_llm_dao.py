import logging
from typing import List

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from api.modules.llm.schema.llm_schema import ResGetLLMS
from config.const import ANALYSIS_ERROR
from database.mariadb.models.resource_llm_model import ResourceLLM

logger = logging.getLogger("app")


async def get_llms(db: Session):
    """
    LLM 목록 조회
    """

    query = select(
        ResourceLLM.code,
        ResourceLLM.name,
        ResourceLLM.is_active,
        ResourceLLM.priority,
        ResourceLLM.created_at,
        ResourceLLM.updated_at,
        ResourceLLM.deleted_at,
    ).order_by(asc(ResourceLLM.priority))

    result = await db.execute(query)
    rows = result.mappings().all()

    return [dict(row) for row in rows]


async def get_first_priority_llm_code(db: Session):
    """
    llm 우선순위 1 llm code 조회
    """
    try:
        query = select(ResourceLLM.code).where(
            ResourceLLM.priority == 1,
            ResourceLLM.deleted_at.is_(None),
            ResourceLLM.is_active == True,
        )

        result = await db.execute(query)
        llm = result.scalars().first()
        if llm == None:
            raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_NOT_EXIST)

        return llm

    except Exception as e:
        logger.error(f"resource_llm 우선순위 조회 중 에러: {e}", exc_info=True)
        raise e
