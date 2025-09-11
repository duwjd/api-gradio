import json

from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.mariadb.models.resource_analysis_model import ResourceAnalysis


async def is_analysis_code(code: str, db: Session):
    """
    분석 코드 체크 (code: AI-ANALYSIS-000001)
    """
    query = select(ResourceAnalysis.code).where(
        ResourceAnalysis.code == code, ResourceAnalysis.is_active == True
    )

    result = await db.execute(query)
    code = result.scalars().first()

    if code:
        return True
    return False


async def get_analysis_group(type: str, db: Session):
    """
    분석 그룹 조회
    """

    query = select(ResourceAnalysis.group).where(ResourceAnalysis.code == type)

    result = await db.execute(query)
    groups = result.scalars().first()

    if not groups or groups == "[]":
        return None
    return groups


async def get_analysis_type(code: str, db: Session):
    """
    analysis type 조회
    """
    query = select(ResourceAnalysis.type).where(
        ResourceAnalysis.code == code, ResourceAnalysis.is_active == True
    )

    result = await db.execute(query)
    type = result.scalars().first()

    if not type:
        return None
    return type


async def get_analysis_dev(db: Session):
    """
    분석 코드 목록 조회 (dev -> local) 복사 전용
    """

    query = select(ResourceAnalysis.__table__)

    result = await db.execute(query)
    rows = result.mappings().all()

    data = [dict(row) for row in rows]

    return data


def update_analysis_sync(analysis: list, local_db: Session):
    """
    resource_analysis 테이블 싱크 업데이트 (dev -> local)
    """

    local_db.execute(delete(ResourceAnalysis))
    local_db.commit()

    for data in analysis:
        group_val = data.get("group")
        if isinstance(group_val, list):
            data["group"] = ",".join(group_val) if group_val else ""

    local_db.bulk_insert_mappings(ResourceAnalysis, analysis)
    local_db.commit()
