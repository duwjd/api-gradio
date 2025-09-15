import asyncio
import logging

from api.modules_master.consumer.master_model_consumer_processor import (
    master_model_cunsumer_sqs_queue_polling,
)
from api.modules_master.consumer.master_api_consumer_processor import (
    master_api_cunsumer_sqs_queue_polling,
)


logger = logging.getLogger("app")


async def master_api_consumer_task_queue():
    """
    master api sqs_queue task 반복 처리
    """

    while True:
        try:
            asyncio.create_task(master_api_cunsumer_sqs_queue_polling())
            await asyncio.sleep(10)

        except Exception as e:
            logger.error(
                f"master api consumer sqs queue 백그라운드 처리 에러: {e}",
                exc_info=True,
            )
            await asyncio.sleep(10)
            raise e


async def master_model_consumer_task_queue():
    """
    master model sqs_queue task 반복 처리
    """

    while True:
        try:
            asyncio.create_task(master_model_cunsumer_sqs_queue_polling())
            await asyncio.sleep(10)

        except Exception as e:
            logger.error(
                f"master model consumer sqs queue 백그라운드 처리 에러: {e}",
                exc_info=True,
            )
            await asyncio.sleep(10)
            raise e
