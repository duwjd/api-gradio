import asyncio
import logging
from datetime import datetime
from typing import Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from api.modules.analysis.dao.analysis_task_gradio_dao import update_task_gradio_progress
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis

logger = logging.getLogger("app")


class ProgressMonitor:
    def __init__(
        self,
        user_id: int,
        project_id: int,
        analysis_code: str,
        progress: int,
        db: AsyncSession,
        task_name="작업 중",
    ):
        self.progress = progress
        self.user_id = user_id
        self.project_id = project_id
        self.analysis_code = analysis_code
        self.task_name = task_name
        self._stop_event = asyncio.Event()
        self._start_time = None
        self.db = db

    def log_bar(self, complete: bool = False):
        bar_len = 30
        filled = int(bar_len * self.progress / 100)
        bar = "█" * filled + "-" * (bar_len - filled)

        if complete and self._start_time:
            elapsed = datetime.now() - self._start_time
            elapsed_str = str(elapsed).split(".")[0]  # hh:mm:ss
            logger.info(
                f"[{self.task_name}] user_id: {self.user_id}, project_id: {self.project_id}, analysis_code: {self.analysis_code}  [{bar}] {self.progress:>3}% 완료 (소요 시간: {elapsed_str})"
            )
        else:
            logger.info(
                f"[{self.task_name}] user_id: {self.user_id}, project_id: {self.project_id}, analysis_code: {self.analysis_code}  [{bar}] {self.progress:>3}%"
            )

    async def start(self):
        self._start_time = datetime.now()
        self.log_bar()
        while self.progress < 99 and not self._stop_event.is_set():
            await asyncio.sleep(5)
            self.progress += 1
            await update_task_gradio_progress(
                req_body=ReqDoAnalysis(
                    userId=self.user_id,
                    projectId=self.project_id,
                    type=self.analysis_code,
                ),
                progress=self.progress,
                db=self.db,
            )
            self.log_bar()
        await self._stop_event.wait()
        self.progress = 100
        self.log_bar(complete=True)

    def stop(self):
        self._stop_event.set()


async def run_with_progress(
    coro: Awaitable,
    user_id: int,
    project_id: int,
    analysis_code: str,
    db: AsyncSession,
    progress: int = 0,
    task_name="작업 중",
) -> Any:
    """
    coroutine과 ProgressMonitor를 병렬 실행하면서 결과 반환 (비동기용)
    """

    async def runner():
        monitor = ProgressMonitor(
            user_id=user_id,
            project_id=project_id,
            analysis_code=analysis_code,
            progress=progress,
            db=db,
            task_name=task_name,
        )
        monitor_task = asyncio.create_task(monitor.start())
        try:
            result = await coro
            return result
        finally:
            monitor.stop()
            await monitor_task

    return await runner()
