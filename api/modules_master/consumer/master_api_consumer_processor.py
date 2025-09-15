import asyncio
import json
import logging
import os

from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)
from api.modules_master.master_service import MasterService
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis

from config.const import SQS_QUEUE, SQS_QUEUE_COUNT
from utils.sqs_util import delete_sqs_message, get_sqs_queue_url, receive_sqs_message

logger = logging.getLogger("app")


async def master_api_cunsumer_sqs_queue_polling():
    try:
        match os.getenv("ENV"):
            case "local":
                queue = SQS_QUEUE.LOCAL_MASTER_REQUEST
            case "development":
                queue = SQS_QUEUE.DEV_MASTER_REQUEST
            case "staging":
                queue = SQS_QUEUE.STG_MASTER_REQUEST
            case "production":
                queue = SQS_QUEUE.PRD_MASTER_REQUEST

        # cunsumer processor 실행
        await master_api_cunsumer_processor(queue)

    except Exception as e:
        logger.error(
            f"master api cunsumer sqs queue polling 중 에러: {e}", exc_info=True
        )


async def master_api_cunsumer_processor(sqs_queue: str):
    """
    api consumer processor
    """

    queue_url = await get_sqs_queue_url(sqs_queue)
    max_processor_count = SQS_QUEUE_COUNT.MAX_MASTER_CONSUMER_COUNT

    # SQS 메시지 가져오기
    messages = await receive_sqs_message(
        queue_url=queue_url,
        max_message_count=max_processor_count,
        VisibilityTimeout=4000,
    )

    logger.info(f"sqs_queue: {sqs_queue}")

    if len(messages) == 0:
        return

    async def handle_message(message: dict):
        try:
            body_raw = message.get("Body")
            body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
            logger.info(
                f"master api consumer message: {json.dumps(body, ensure_ascii=False)}"
            )

            req_body = ReqDoAnalysis(**body)

            # 비디오 요청 폴링 처리
            await MasterService.video_polling(req_body)

            # 메시지 삭제
            await delete_sqs_message(queue_url, message)

            logger.info(
                f"api consumer {json.dumps(message, ensure_ascii=False)} 메시지 삭제 완료"
            )
        except Exception as e:
            logger.error(
                f"api consumer 메시지 처리 실패: {e} | message={message}", exc_info=True
            )
            # 메시지 삭제
            await delete_sqs_message(queue_url, message)

    # 메시지 병렬 처리
    await asyncio.gather(
        *(handle_message(message) for message in messages), return_exceptions=True
    )


# async def master_model_consumer_processor_parallel(sqs_queues: list[str]):
#     """
#     api cunsumer SQS Queue를 병렬 처리
#     """
#     tasks = [master_api_cunsumer_processor(queue_name) for queue_name in sqs_queues]
#     await asyncio.gather(*tasks)
