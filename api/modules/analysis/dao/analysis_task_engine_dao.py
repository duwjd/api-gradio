import json

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from database.mariadb.mariadb_config import AsyncSessionLocal
from database.mariadb.models.task_engine_model import TaskEngine


async def get_process_done_count(req_body: ReqDoAnalysis):
    """
    task_engine 하나의 분석요청 완료된 프로세스 개수 조회

    Args:
        req_body (ReqDoAnalysis): req_body
    """

    async with AsyncSessionLocal() as db:
        user_id = req_body.userId
        project_id = req_body.projectId
        analysis_code = req_body.type

        query = (
            select(func.count())
            .select_from(TaskEngine)
            .where(
                TaskEngine.user_id == user_id,
                TaskEngine.project_id == project_id,
                TaskEngine.analysis_code == analysis_code,
                TaskEngine.status == "success",
            )
        )

        result = await db.execute(query)
        count = result.scalar() or 0
        return count


async def is_process_fail(req_body: ReqDoAnalysis):
    """
    task_engine 실패 확인

    Args:
        req_body (ReqDoAnalysis): req_body
    """
    async with AsyncSessionLocal() as db:
        user_id = req_body.userId
        project_id = req_body.projectId
        analysis_code = req_body.type

        query = (
            select(func.count())
            .select_from(TaskEngine)
            .where(
                TaskEngine.user_id == user_id,
                TaskEngine.project_id == project_id,
                TaskEngine.analysis_code == analysis_code,
                TaskEngine.status == "fail",
            )
        )

        result = await db.execute(query)
        count = result.scalar() or 0

        if count > 0:
            return True
        return False


async def get_task_engine_all_result(req_body: ReqDoAnalysis):
    """
    task_engine user_id, project_id, analysis_code 조건 결과 데이터 조회

    Args:
        req_body (ReqDoAnalysis): req_body
    """

    async with AsyncSessionLocal() as db:
        user_id = req_body.userId
        project_id = req_body.projectId
        analysis_code = req_body.type

        query = (
            select(TaskEngine.result)
            .where(
                TaskEngine.user_id == user_id,
                TaskEngine.project_id == project_id,
                TaskEngine.analysis_code == analysis_code,
            )
            .order_by(TaskEngine.order_no.asc())
        )

        result = await db.execute(query)
        rows = result.mappings().all()

        response_data = [json.loads(row["result"])["video"] for row in rows]
        return response_data


async def delete_task_engine(req_body: ReqDoAnalysis, db: Session):
    """
    task_engine 데이터 있을 시 삭제

    Args:
        req_body (ReqDoAnalysis): req_body
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    query = delete(TaskEngine).where(
        TaskEngine.user_id == user_id,
        TaskEngine.project_id == project_id,
        TaskEngine.analysis_code == analysis_code,
    )

    await db.execute(query)
    await db.commit()
