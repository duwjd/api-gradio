import json
from datetime import datetime

from sqlalchemy import delete, desc, func, literal_column, select, update, or_
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from api.modules_op.schema.op_analysis_schema import (
    ReqUpdateAnalysis,
    ResGetAnalysisCodes,
)
from database.mariadb.models.resource_analysis_model import ResourceAnalysis
from database.mariadb.models.task_llm_model import TaskLLM


async def is_analysis_code(code: str, db: Session):
    """
    op 분석 타입 체크
    """

    query = select(ResourceAnalysis).where(ResourceAnalysis.code == code)

    result = await db.execute(query)
    code = result.scalars().first()

    if code:
        return True
    return False


async def create_last_code(type: str, db: Session) -> str:
    """
    op
    특정 type에 대한 마지막 code를 조회하고, 없으면 000001로 시작.
    기존 코드가 있으면 숫자 부분을 +1 하여 새 코드 생성.
    """
    query = (
        select(ResourceAnalysis.code)
        .where(ResourceAnalysis.type == type)
        .order_by(desc(ResourceAnalysis.code))
        .limit(1)
    )

    result = await db.execute(query)
    latest_code = result.scalar_one_or_none()

    prefix = f"AI-{type.upper()}-"

    if latest_code is None:
        return f"{prefix}000001"

    # 숫자 부분만 추출
    try:
        last_number = int(latest_code.split("-")[-1])
    except (ValueError, IndexError):
        # 혹시 형식이 깨진 경우 대비 (예외 처리)
        last_number = 0

    # +1 하고 zero-padding (6자리)
    new_code = f"{prefix}{last_number + 1:06d}"
    return new_code


async def create_analysis_code(code: str, type: str, db: Session) -> str:
    """
    op 분석 코드 생성
    """
    query = insert(ResourceAnalysis).values(code=code, type=type)
    await db.execute(query)
    await db.commit()


async def get_analysis_code(code: str, db: Session):
    """
    op 분석 코드 조회
    """
    query = select(ResourceAnalysis).where(
        ResourceAnalysis.code == code, ResourceAnalysis.deleted_at.is_(None)
    )

    result = await db.execute(query)
    analysis = result.scalars().first()

    if analysis:
        return analysis.type
    return None


async def get_analysis_group(code: str, db: Session):
    """
    op 분석 코드 조회
    """
    query = select(ResourceAnalysis).where(
        ResourceAnalysis.code == code, ResourceAnalysis.deleted_at.is_(None)
    )

    result = await db.execute(query)
    analysis = result.scalars().first()

    if analysis:
        return analysis.group
    return None


async def get_analysis(db: Session):
    """
    op 분석 코드 전체 조회
    """

    query = select(ResourceAnalysis)
    result = await db.execute(query)
    rows = result.mappings().all()

    return [
        {
            k: v
            for k, v in row["ResourceAnalysis"].__dict__.items()
            if k != "_sa_instance_state"
        }
        for row in rows
    ]


async def get_analysis_codes(db: Session):
    """
    op 분석 코드 목록 조회
    """

    query = select(
        ResourceAnalysis.code,
        ResourceAnalysis.type,
        ResourceAnalysis.group,
        ResourceAnalysis.name,
        ResourceAnalysis.is_active,
        getattr(ResourceAnalysis, "created_at"),
        getattr(ResourceAnalysis, "updated_at"),
    ).where(ResourceAnalysis.deleted_at.is_(None))

    result = await db.execute(query)
    rows = result.mappings().all()

    response_data = [
        ResGetAnalysisCodes(
            code=row["code"],
            type=row["type"],
            group=(
                json.loads(row["group"])
                if isinstance(row["group"], str)
                else row["group"]
            ),
            name=row["name"],
            is_active=row["is_active"],
            created_at=row["created_at"].isoformat() if row["created_at"] else None,
            updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
        ).model_dump()
        for row in rows
    ]

    return response_data


async def get_analysis_type_codes(type: str, db: Session):
    """
    op 분석 코드 type 목록 조회
    """

    query = select(
        ResourceAnalysis.code,
        ResourceAnalysis.type,
        ResourceAnalysis.group,
        ResourceAnalysis.name,
        ResourceAnalysis.is_active,
        getattr(ResourceAnalysis, "created_at"),
        getattr(ResourceAnalysis, "updated_at"),
    ).where(ResourceAnalysis.type == type, ResourceAnalysis.deleted_at.is_(None))

    result = await db.execute(query)
    rows = result.mappings().all()

    response_data = [
        ResGetAnalysisCodes(
            code=row["code"],
            type=row["type"],
            group=(
                json.loads(row["group"])
                if isinstance(row["group"], str)
                else row["group"]
            ),
            name=row["name"],
            is_active=row["is_active"],
            created_at=row["created_at"].isoformat() if row["created_at"] else None,
            updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
        ).model_dump()
        for row in rows
    ]

    return response_data


async def update_analysis(req_body: ReqUpdateAnalysis, db: Session):
    """
    op 분석 수정
    """
    update_data = req_body.model_dump(exclude_none=True)
    code = update_data.pop("code")

    if "group" in update_data:
        update_data["group"] = json.dumps(update_data["group"])

    query = (
        update(ResourceAnalysis)
        .where(ResourceAnalysis.code == code)
        .values(**update_data)
    )

    await db.execute(query)
    await db.commit()


async def delete_analysis(code: str, db: Session):
    """
    op 분석 삭제
    """
    query = (
        update(ResourceAnalysis)
        .where(ResourceAnalysis.code == code)
        .values(deleted_at=datetime.utcnow())
    )
    await db.execute(query)
    await db.commit()


async def deploy_analysis(deploy_data: list[dict], db: Session):
    """
    op 분석 배포 (bulk upsert + 나머지 삭제)
    """
    # JSON 직렬화
    for row in deploy_data:
        if "group" in row and isinstance(row["group"], (dict, list)):
            row["group"] = json.dumps(row["group"])

    # 추출된 코드 목록
    incoming_codes = [row["code"] for row in deploy_data]

    # UPSERT
    stmt = insert(ResourceAnalysis).values(deploy_data)

    update_keys = set(deploy_data[0].keys()) - {"code"}
    RESERVED_KEYWORDS = {"group", "type"}

    update_data = {
        key: literal_column(
            f"VALUES(`{key}`)" if key in RESERVED_KEYWORDS else f"VALUES({key})"
        )
        for key in update_keys
    }

    stmt = stmt.on_duplicate_key_update(**update_data)
    await db.execute(stmt)

    # DELETE: 기존 DB에서 deploy_data에 없는 code 삭제
    delete_stmt = delete(ResourceAnalysis).where(
        ResourceAnalysis.code.not_in(incoming_codes)
    )
    await db.execute(delete_stmt)
    await db.commit()


async def op_get_analysis_task_status_count(status: str, db: Session):
    """
    analysis status 수
    """
    # status progress count
    query = (
        select(func.count())
        .select_from(TaskLLM)
        .where(
            TaskLLM.status == status,
            or_(
                TaskLLM.analysis_code == "AI-PHOTO2VIDEO-000001",
                TaskLLM.analysis_code == "AI-VIDEO-GEN-000001",
            ),
        )
    )

    result = await db.execute(query)
    count = result.scalar() or 0

    return count
