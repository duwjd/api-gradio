import asyncio
import json
import logging
import os

from api.modules.analysis.analysis_service import AnalysisService
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from config.const import SQS_QUEUE, SQS_QUEUE_COUNT
from utils.sqs_util import delete_sqs_message, get_sqs_queue_url, receive_sqs_message

logger = logging.getLogger("app")


async def analysis_cunsumer_sqs_queue_polling():

    try:
        match os.getenv("ENV"):
            case "gradio":
                queue = SQS_QUEUE.GRADIO_ANALYSIS_REQUEST
            case "local":
                queue = SQS_QUEUE.LOCAL_ANALYSIS_REQUEST
            case "development":
                queue = SQS_QUEUE.DEV_ANALYSIS_REQUEST
            case "staging":
                queue = SQS_QUEUE.STG_ANALYSIS_REQUEST
            case "production":
                queue = SQS_QUEUE.PRD_ANALYSIS_REQUEST
        logger.info(f"analysis cunsumer sqs queues : {queue}")

        # cunsumer processor 실행
        await analysis_cunsumer_processor(queue)

    except Exception as e:
        logger.error(f"analysis cunsumer sqs queue polling 중 에러: {e}", exc_info=True)
        raise e


async def analysis_cunsumer_processor(sqs_queue: str):
    """
    consumer processor 분기 처리
    """

    queue_url = await get_sqs_queue_url(sqs_queue)
    max_processor_count = SQS_QUEUE_COUNT.MAX_ANALYSIS_CONSUMER_COUNT

    # SQS 메시지 가져오기
    messages = await receive_sqs_message(queue_url, max_processor_count)
    if len(messages) == 0:
        return

    logger.info(f"sqs_queue: {sqs_queue}")

    async def handle_message(message: dict):
        try:
            body_raw = message.get("Body")
            body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
            logger.info(
                f"analysis consumer message body: {json.dumps(body, ensure_ascii=False, default=str)}"
            )

            req_body = ReqDoAnalysis(**body)

            # 분석 완료 처리
            await AnalysisService.do_analysis(req_body)

            # 메시지 삭제
            await delete_sqs_message(queue_url, message)
            logger.info(
                f"analysis consumer {json.dumps(message, ensure_ascii=False, default=str)} 메시지 삭제 완료"
            )
        except Exception as e:
            logger.error(
                f"analysis consumer 메시지 처리 실패: {e} | message={body_raw}",
                exc_info=True,
            )

            # 메시지 삭제 (실패한 경우도 삭제할지 재시도 큐로 넘길지 정책 필요)
            await delete_sqs_message(queue_url, message)

    # 메시지 병렬 처리
    await asyncio.gather(*(handle_message(message) for message in messages))


# async def analysis_cunsumer_processor_parallel(sqs_queues: list[str]):
#     """
#     cunsumer SQS Queue를 병렬 처리
#     """
#     tasks = [analysis_cunsumer_processor(queue_name) for queue_name in sqs_queues]
#     await asyncio.gather(*tasks)
