import json

from sqlalchemy import delete, func, select, update
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)
from config.const import STATUS
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


async def get_task_engine_all_result(req_body: ReqConsumerAnalysis):
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


async def init_task_engine(
    req_body: ReqDoAnalysis, order_no: int, process: str, db: Session
):
    """
    task engine 생성

    Args:
        req_body (ReqDoAnalysis): req_body
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = TaskEngine(
        user_id=user_id,
        project_id=project_id,
        analysis_code=analysis_code,
        status=STATUS.PROGRESS,
        progress=0,
        process=process,
        order_no=order_no,
    )

    db.add(task)
    await db.commit()


async def update_task_engine_result(
    req_body: ReqDoAnalysis,
    order_no: int,
    status: str,
    progress: int,
    result: str,
    db: Session,
):
    """
    task_engine 수정

    Args:
        req_body (ReqDoAnalysis): req_body

        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    query = (
        update(TaskEngine)
        .where(
            TaskEngine.user_id == user_id,
            TaskEngine.project_id == project_id,
            TaskEngine.analysis_code == analysis_code,
            TaskEngine.order_no == order_no,
        )
        .values(status=status, progress=progress, result=result)
    )

    await db.execute(query)


async def get_task_engine_status(req_body: ReqDoAnalysis, db: Session):
    """
    task_engine 상태 조회
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    query = select(TaskEngine.status).where(
        TaskEngine.user_id == user_id,
        TaskEngine.project_id == project_id,
        TaskEngine.analysis_code == analysis_code,
    )
    result = await db.execute(query)
    return result.scalars().first()


async def update_task_engine_init_error(req_body: ReqDoAnalysis, db: Session):
    """
    task_engine 성공 시 에러 메세지 초기화

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = getattr(req_body, "analysisCode", None) or req_body.type

    task = (
        update(TaskEngine)
        .where(
            TaskEngine.user_id == user_id,
            TaskEngine.project_id == project_id,
            TaskEngine.analysis_code == analysis_code,
        )
        .values(error_code=None, error_message=None)
    )
    await db.execute(task)
    await db.commit()


async def update_task_engine_error(
    req_body: ReqDoAnalysis, error_code: str, error_message: str, db: Session
):
    """
    task_engine 에러 수정

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = getattr(req_body, "analysisCode", None) or req_body.type

    task = (
        update(TaskEngine)
        .where(
            TaskEngine.user_id == user_id,
            TaskEngine.project_id == project_id,
            TaskEngine.analysis_code == analysis_code,
        )
        .values(error_code=error_code, error_message=error_message)
    )
    await db.execute(task)
    await db.commit()


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
