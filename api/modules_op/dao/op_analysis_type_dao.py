from datetime import datetime

from sqlalchemy import delete, literal_column, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from api.modules.analysis.schema.analysis_schema import ResGetAnalysisTypes
from api.modules_op.schema.op_analyis_type_schema import (
    ReqCreateAnalysisType,
    ReqDeleteAnalysisType,
    ResGetAnalysisTypes,
)
from database.mariadb.models.resource_analysis_type_model import ResourceAnalysisType


async def is_analysis_type(type: str, db: Session):
    """
    op 분석 타입 체크
    """

    query = select(ResourceAnalysisType).where(
        ResourceAnalysisType.type == type, ResourceAnalysisType.deleted_at.is_(None)
    )

    result = await db.execute(query)
    analysis = result.scalars().first()

    if analysis:
        return True
    return False


async def create_analysis_type(req_body: ReqCreateAnalysisType, db: Session):
    """
    op 분석 타입 생성
    """
    type = req_body.type
    query = insert(ResourceAnalysisType).values(type=type)

    await db.execute(query)
    await db.commit()


async def get_analysis_types(db: Session):
    """
    op 분석 타입 목록 조회
    """
    query = select(
        ResourceAnalysisType.type,
        ResourceAnalysisType.name,
        getattr(ResourceAnalysisType, "created_at"),
        getattr(ResourceAnalysisType, "updated_at"),
    ).where(ResourceAnalysisType.deleted_at.is_(None))

    result = await db.execute(query)
    rows = result.mappings().all()

    response_data = [
        ResGetAnalysisTypes(
            type=row["type"],
            name=row["name"],
            created_at=row["created_at"].isoformat() if row["created_at"] else None,
            updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
        ).model_dump()
        for row in rows
    ]

    return response_data


async def update_analysis_type(req_body: ResourceAnalysisType, db: Session):
    """
    op 분석 타입 수정
    """

    analysis_type = req_body.type
    analysis_name = req_body.name

    query = (
        update(ResourceAnalysisType)
        .where(ResourceAnalysisType.type == analysis_type)
        .values(name=analysis_name)
    )

    await db.execute(query)
    await db.commit()


async def delete_analysis_type(req_body: ReqDeleteAnalysisType, db: Session):
    """
    op 분석 타입 삭제
    """
    type = req_body.type
    query = (
        update(ResourceAnalysisType)
        .where(ResourceAnalysisType.type == type)
        .values(deleted_at=datetime.utcnow())
    )

    await db.execute(query)
    await db.commit()


async def deploy_analysis_type(deploy_data: list[dict], db: Session):
    """
    op 분석 타입 배포 (bulk upsert + 누락된 항목 삭제)
    """
    if not deploy_data:
        return

    # 추출된 코드 목록
    incoming_types = [row["type"] for row in deploy_data]

    # UPSERT 구성
    stmt = insert(ResourceAnalysisType).values(deploy_data)
    update_keys = set(deploy_data[0].keys()) - {"type"}  # type은 PK

    stmt = stmt.on_duplicate_key_update(
        {key: literal_column(f"VALUES({key})") for key in update_keys}
    )

    # UPSERT 실행
    await db.execute(stmt)

    # 기존 DB에 존재하나, incoming_types에 없는 항목 삭제
    delete_stmt = delete(ResourceAnalysisType).where(
        ResourceAnalysisType.type.notin_(incoming_types)
    )
    await db.execute(delete_stmt)
    await db.commit()
