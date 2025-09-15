import asyncio
import logging

from api.modules.analysis.consumer.analysis_consumer_processor import (
    analysis_cunsumer_sqs_queue_polling,
)

logger = logging.getLogger("app")


async def analysis_consumer_task_queue():
    """
    sqs_queue consumer task 반복 처리
    """

    while True:
        try:
            asyncio.create_task(analysis_cunsumer_sqs_queue_polling())
            await asyncio.sleep(10)

        except Exception as e:
            logger.error(
                f"analysis consumer sqs queue 백그라운드 처리 에러: {e}", exc_info=True
            )
            await asyncio.sleep(10)
            raise e
