import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from api.modules.analysis.analysis_service import AnalysisService
from api.modules.analysis.dao.analysis_sqs_queue_dao import (
    get_analysis_producer_sqs_queue,
)
from api.modules.analysis.dao.analysis_task_engine_dao import (
    get_process_done_count,
    is_process_fail,
)
from api.modules.analysis.dao.analysis_task_llm_dao import (
    get_task_llm_progress,
    update_task_llm_progress,
)
from api.modules.analysis.schema.analysis_schema import (
    ReqDoAnalysis,
    ResAnalysisSQSConsumer,
    ResGetWanSQSQueueCount,
)
from api.modules_master.consumer.dao.master_dao import (
    get_task_engine_progress_avg,
    get_worker_count,
)
from config.const import AI_MODEL, ANALYSIS_ERROR, SQS_QUEUE, STATUS
from database.mariadb.mariadb_config import AsyncSessionLocal
from utils.sqs_util import send_sqs_message

logger = logging.getLogger("app")


class MasterService:
    @staticmethod
    async def video_polling(
        req_body: ReqDoAnalysis,
        timeout: Optional[int] = 4000,
    ):
        """
        모델 비디오 생성 폴링 처리 (타임아웃 포함)

        Args:
            req_body (ReqDoAnalysis): req_body
            timeout (int): 최대 대기 시간 (초), 기본 5분
        """

        async def _polling():
            # 분석 조회 SQS queue
            logger.info(f"api consumer 비디오 폴링 시작")

            analysis_producer_sqs_queue = await get_analysis_producer_sqs_queue()
            init_expected_minutes = await MasterService.init_expected_minutes()

            # 시작 시간 기록
            start_time = datetime.utcnow()

            async with AsyncSessionLocal() as db:
                progress = await get_task_llm_progress(req_body, db)
            if progress < 100:
                while True:
                    process_fail = await is_process_fail(req_body)
                    if process_fail == True:
                        break

                    # task_engine 완료 카운트 조회
                    wan_done_count = await get_process_done_count(req_body)
                    if wan_done_count == len(req_body.documentS3):
                        logger.info(f"{AI_MODEL.WAN} 모델 실행 완료")
                        break

                    # task_engine progress 평균 구하기
                    progress_avg = progress + await get_task_engine_progress_avg(
                        req_body
                    )

                    # 경과 시간 계산
                    elapsed_seconds = (datetime.utcnow() - start_time).total_seconds()
                    elapsed_minutes = int(elapsed_seconds // 60)
                    expected_minutes = max(init_expected_minutes - elapsed_minutes, 1)

                    if progress_avg < 100 and progress_avg > 0:
                        # progress 저장
                        async with AsyncSessionLocal() as db:
                            await update_task_llm_progress(req_body, progress_avg, db)

                        await send_sqs_message(
                            analysis_producer_sqs_queue,
                            message=ResAnalysisSQSConsumer(
                                httpStatusCode=200,
                                userId=req_body.userId,
                                projectId=req_body.projectId,
                                type=req_body.type,
                                status=STATUS.PROGRESS,
                                progress=progress_avg,
                                expectedMinutes=expected_minutes,
                            ).model_dump_json(exclude_none=True),
                        )

                    else:
                        break

                    await asyncio.sleep(5)

        try:
            return await asyncio.wait_for(_polling(), timeout=timeout)

        except Exception as e:
            logger.error(f"master 모델 비디오 폴링 중 에러: {e}", exc_info=True)
            raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_FAIL)

    @staticmethod
    async def init_expected_minutes():
        """
        예상 분석 시간(분) 구하기
        """
        sqs_queue_count = await MasterService.get_analysis_task_pending_count()

        # ((사용가능 메세지 + 이동중인 메세지 ) *7분 / 서버 대수)
        expected_minute = ((sqs_queue_count.pending + sqs_queue_count.progress) * 7) / 4
        if expected_minute == 0:
            return 7
        return ((sqs_queue_count.pending + sqs_queue_count.progress) * 7) / 4

    @staticmethod
    async def get_analysis_task_pending_count():
        env = os.getenv("ENV")
        match env:
            case "gradio":
                sqs_queue_count = await AnalysisService.get_model_sqs_queue_count(
                    SQS_QUEUE.GRADIO_ANALYSIS_REQUEST
                )
            case "local":
                sqs_queue_count = await AnalysisService.get_model_sqs_queue_count(
                    SQS_QUEUE.LOCAL_ANALYSIS_REQUEST
                )
            case "development":
                sqs_queue_count = await AnalysisService.get_model_sqs_queue_count(
                    SQS_QUEUE.DEV_ANALYSIS_REQUEST
                )
            case "staging":
                sqs_queue_count = await AnalysisService.get_model_sqs_queue_count(
                    SQS_QUEUE.STG_ANALYSIS_REQUEST
                )
            case "production":
                sqs_queue_count = await AnalysisService.get_model_sqs_queue_count(
                    SQS_QUEUE.PRD_ANALYSIS_REQUEST
                )
        return sqs_queue_count
