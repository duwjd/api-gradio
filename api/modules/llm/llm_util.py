import asyncio
import logging

from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_task_llm_dao import (
    get_task_llm_progress,
    update_task_llm_progress,
)
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis

logger = logging.getLogger("app")
logger.propagate = False


async def update_progress_background(
    req_body: ReqDoAnalysis,
    db: Session,
    event: asyncio.Event,
    start_progress: int = None,
    end_progress: int = None,
):
    """
    백그라운드에서 주기적으로 task_llm progress를 갱신합니다.
    """
    try:
        progress = await get_task_llm_progress(req_body, db)

        if start_progress == None or end_progress == None:
            while not event.is_set():
                if progress < 95:
                    progress += 5
                    await update_task_llm_progress(req_body, progress, db)

                await asyncio.sleep(2)  # 2초마다 갱신
        else:
            progress = start_progress
            while not event.is_set():
                if progress < end_progress and progress < 95:
                    progress += 5
                    await update_task_llm_progress(req_body, progress, db)
                else:
                    logger.info(
                        f"[분석 진행률] user_id: {req_body.userId}, project_id: {req_body.projectId}, analysis_code: {req_body.type}, progress: {progress}"
                    )
                await asyncio.sleep(2)  # 2초마다 갱신
    except Exception as e:
        logger.warning(f"[progress] update failed: {e}")
