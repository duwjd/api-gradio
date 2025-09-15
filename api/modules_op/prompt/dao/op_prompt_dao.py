import json
import logging
from datetime import datetime

from sqlalchemy import delete, desc, func, literal_column, or_, select, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from api.modules_op.dao.op_analysis_dao import create_last_code
from api.modules_op.prompt.scema.op_prompt_schema import (
    ReqOpCreatePrompt,
    ReqOpDeletePrompt,
    ReqOpGetPrompt,
    ReqOpUpdatePrompt,
)
from database.mariadb.models.resource_prompt_model import ResourcePrompt

logger = logging.getLogger("app")


async def create_last_prompt_code(db: Session) -> str:
    """
    op
    특정 type에 대한 마지막 code를 조회하고, 없으면 000001로 시작.
    기존 코드가 있으면 숫자 부분을 +1 하여 새 코드 생성.
    """
    query = select(ResourcePrompt.code).order_by(desc(ResourcePrompt.code)).limit(1)

    result = await db.execute(query)
    latest_code = result.scalar_one_or_none()

    prefix = f"AI-PROMPT-"

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


async def is_prompt_analyis_code_exist(
    analysis_code: str, llm_code: str, db: Session
) -> bool:
    """
    OP Prompt 분석 코드 검사
    """
    prompts = await op_get_prompts(db)
    for prompt in prompts:
        if prompt["analysis_code"] == analysis_code and prompt["llm_code"] == llm_code:
            return True
    return False


async def op_create_prompt(
    group: str, analysis_code: str, code: str, llm_code: str, db: Session
):
    """
    OP Prompt 생성
    """

    query = insert(ResourcePrompt).values(
        code=code,
        group=group,
        analysis_code=analysis_code,
        llm_code=llm_code,
    )

    await db.execute(query)
    await db.commit()


async def op_get_prompts(db: Session):
    """
    OP Prompt 전체 조회
    """
    query = select(ResourcePrompt)
    result = await db.execute(query)
    rows = result.mappings().all()

    prompts: list[dict] = []
    for row in rows:
        data = {
            k: v
            for k, v in row["ResourcePrompt"].__dict__.items()
            if k != "_sa_instance_state"
        }

        # group 필드가 문자열(JSON string)이면 파싱
        if data.get("group"):
            try:
                data["group"] = json.loads(data["group"])
            except Exception:
                # 혹시 JSON 형식이 아니면 그냥 리스트로 감쌈
                data["group"] = [data["group"]]

        prompts.append(data)

    return prompts


async def op_get_prompt(req_query: ReqOpGetPrompt, db: Session):
    """
    OP Prompt 조회
    """

    llm_code = req_query.llm_code
    group = req_query.group
    analysis_code = req_query.analysis_code

    if group == "common":
        group_query = ResourcePrompt.group == "[]"
    else:
        group_query = ResourcePrompt.group.like(f'%"{group}"%')
    query = select(
        ResourcePrompt.prompt,
    ).where(
        ResourcePrompt.llm_code == llm_code,
        ResourcePrompt.analysis_code == analysis_code,
        group_query,
    )

    result = await db.execute(query)
    prompt = result.scalars().first()

    if prompt:
        if analysis_code.startswith("AI-ASSIST"):
            return prompt
        return json.loads(prompt)
    return None


async def op_update_prompt(req_body: ReqOpUpdatePrompt, db: Session):
    """
    OP Prompt 수정
    """
    llm_code = req_body.llm_code
    group = req_body.group
    analysis_code = req_body.analysis_code
    prompt = req_body.prompt

    if group == "common":
        group_query = ResourcePrompt.group == "[]"
    else:
        group_query = ResourcePrompt.group.like(f'%"{group}"%')

    query = (
        update(ResourcePrompt)
        .where(
            ResourcePrompt.llm_code == llm_code,
            ResourcePrompt.analysis_code == analysis_code,
            group_query,
        )
        .values(prompt=prompt)
    )

    row = await db.execute(query)
    await db.commit()

    if row.rowcount > 0:
        return True
    return False


async def op_delete_prompt(req_body: ReqOpDeletePrompt, db: Session):
    """
    OP Prompt 삭제
    """
    analysis_code = req_body.analysis_code

    query = delete(ResourcePrompt).where(
        ResourcePrompt.analysis_code == analysis_code,
    )

    row = await db.execute(query)
    await db.commit()

    if row.rowcount > 0:
        return True
    return False


async def op_deploy_prompt(deploy_data: list[dict], db: Session):
    """
    OP Prompt 삭제
    """

    # # 1) group JSON 직렬화
    for row in deploy_data:
        if "group" in row and isinstance(row["group"], (dict, list)):
            row["group"] = json.dumps(row["group"])

    # 2) 추출된 code 목록
    incoming_codes = [row["code"] for row in deploy_data]

    # 3) UPSERT (ON DUPLICATE KEY UPDATE)
    stmt = insert(ResourcePrompt).values(deploy_data)

    update_keys = set(deploy_data[0].keys()) - {"code"}

    update_data = {key: stmt.inserted[key] for key in update_keys}

    stmt = stmt.on_duplicate_key_update(**update_data)
    await db.execute(stmt)

    # 4) DELETE (배포되지 않은 code 제거)
    delete_stmt = delete(ResourcePrompt).where(~ResourcePrompt.code.in_(incoming_codes))
    await db.execute(delete_stmt)

    # 5) Commit
    await db.commit()
