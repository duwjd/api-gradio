import asyncio
import json
import logging
import os

from sqlalchemy.orm import Session

from api.modules.analysis.analysis_complate_service import AnalysisComplateService
from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)
from api.modules.analysis.dao.analysis_task_llm_dao import get_task_llm_progress
from config.const import SQS_QUEUE, SQS_QUEUE_COUNT
from utils.sqs_util import delete_sqs_message, get_sqs_queue_url, receive_sqs_message

logger = logging.getLogger("app")


async def master_model_cunsumer_sqs_queue_polling():
    try:
        match os.getenv("ENV"):
            case "gradio":
                #2.2인지 2.1인지 구별
                if get_task_llm_progress() == "WAN2.2":
                    queue = SQS_QUEUE.GRADIO_WAN_2_2_RESPONSE
                elif get_task_llm_progress() == "WAN2.1":
                    queue = SQS_QUEUE.GRADIO_WAN_2_1_RESPONSE
            case "local":
                queue = SQS_QUEUE.LOCAL_WAN_RESPONSE
            case "development":
                queue = SQS_QUEUE.DEV_WAN_RESPONSE
            case "staging":
                queue = SQS_QUEUE.STG_WAN_RESPONSE
            case "production":
                queue = SQS_QUEUE.PRD_WAN_RESPONSE

        # cunsumer processor 실행
        await master_model_cunsumer_processor(queue)
    except Exception as e:
        logger.error(
            f"master model cunsumer sqs queue polling 중 에러: {e}", exc_info=True
        )


async def master_model_cunsumer_processor(sqs_queue: str):
    """
    model consumer processor
    """

    queue_url = await get_sqs_queue_url(sqs_queue)
    max_processor_count = SQS_QUEUE_COUNT.MAX_MASTER_CONSUMER_COUNT

    # SQS 메시지 가져오기
    messages = await receive_sqs_message(queue_url, max_processor_count)

    logger.info(f"sqs_queue: {sqs_queue}")

    if len(messages) == 0:
        return

    async def handle_message(message: dict):
        try:
            body_raw = message.get("Body")
            body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
            logger.info(
                f"master model consumer message: {json.dumps(body, ensure_ascii=False)}"
            )

            req_body = ReqConsumerAnalysis(**body)

            # 분석 완료 처리
            await AnalysisComplateService.analysis_complate(req_body)

            # 메시지 삭제
            await delete_sqs_message(queue_url, message)
            logger.info(
                f"model consumer {json.dumps(message, ensure_ascii=False)} 메시지 삭제 완료"
            )
        except Exception as e:
            logger.error(
                f"model consumer 메시지 처리 실패: {e} | message={message}",
                exc_info=True,
            )

            await delete_sqs_message(queue_url, message)

    # 메시지 병렬 처리
    await asyncio.gather(
        *(handle_message(message) for message in messages), return_exceptions=True
    )


# async def master_model_consumer_processor_parallel(sqs_queues: list[str]):
#     """
#     model cunsumer SQS Queue를 병렬 처리
#     """
#     tasks = [master_model_cunsumer_processor(queue_name) for queue_name in sqs_queues]
#     await asyncio.gather(*tasks)
