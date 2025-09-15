import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from database.mariadb.mariadb_config import AsyncSessionLocal
from database.mariadb.models.resource_worker_model import ResourceWorker
from database.mariadb.models.task_engine_model import TaskEngine

logger = logging.getLogger("app")


async def get_task_engine_progress_avg(req_body: ReqDoAnalysis):
    """
    task_engine progress 평균 구하기
    """
    async with AsyncSessionLocal() as db:
        query = select(TaskEngine.progress).where(
            TaskEngine.user_id == req_body.userId,
            TaskEngine.project_id == req_body.projectId,
            TaskEngine.analysis_code == req_body.type,
        )
        result = await db.execute(query)
        rows = result.scalars().all()
        if not rows:
            return 0  # 값이 없을 때 0 반환 (예외 방지)

        avg = sum(rows) / len(rows)
        return int(avg)


async def get_worker_count():
    """
    worker 개수 조회
    """
    async with AsyncSessionLocal() as db:
        query = select(ResourceWorker)
        result = await db.execute(query)
        rows = result.scalars().all()

        return len(rows)
