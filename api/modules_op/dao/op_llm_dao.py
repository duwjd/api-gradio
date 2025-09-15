from typing import List

from sqlalchemy import asc, select, update
from sqlalchemy.orm import Session

from api.modules_op.schema.op_llm_schema import ReqUpdateLLM
from database.mariadb.models.resource_llm_model import ResourceLLM


async def op_get_llms(db: Session):
    """
    op LLM 목록 조회
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


async def op_update_llm(req_body: List[ReqUpdateLLM], db: Session):
    """
    op LLM 수정
    """

    for req in req_body:
        query = (
            update(ResourceLLM)
            .where(ResourceLLM.code == req.code)
            .values(priority=req.priority, is_active=req.is_active)
        )

        await db.execute(query)
        await db.commit()
