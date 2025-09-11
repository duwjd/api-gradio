import logging

from sqlalchemy import or_, update

from database.mariadb.mariadb_config import SessionLocal
from database.mariadb.models.task_llm_model import TaskLLM

logger = logging.getLogger("app")


def task_llm_progress_to_fail():
    """
    서버 시작 시 task_llm progress -> fail 로 변경
    """
    with SessionLocal() as db:
        task = (
            update(TaskLLM)
            .where(or_(TaskLLM.status == "progress", TaskLLM.status == "pending"))
            .values(
                status="fail",
                progress=0,
                error_code="AI_API_ANALYSIS_RESPONSE_FAIL",
            )
        )

        db.execute(task)
        db.commit()

        logger.info("task_llm progress -> fail로 변경")
