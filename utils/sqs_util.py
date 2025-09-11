import logging
import os
import uuid

import aioboto3
from api.modules.analysis.schema.analysis_schema import (
    ResGetWanSQSQueueCount,
)

logger = logging.getLogger("app")


async def get_sqs_client():
    """
    SQS 클라이언트 가져오기
    """
    session = aioboto3.Session()
    return session.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )


async def send_sqs_message(queue_url: str, message: str):
    """
    SQS 메세지 전송
    """
    try:
        async with await get_sqs_client() as client:
            await client.send_message(
                QueueUrl=queue_url,
                MessageBody=message,
                MessageGroupId=str(uuid.uuid4()),
                MessageDeduplicationId=str(uuid.uuid4()),
            )

            logger.info(f"SQS 메세지 전송 완료: {message}")

    except Exception as e:
        logger.error(f"SQS 메세지 전송 오류: {e}", exc_info=True)
        raise e


async def get_sqs_queue_url(queue_name: str):
    """
    SQS큐 URL 가져오기
    """
    async with await get_sqs_client() as client:
        response = await client.get_queue_url(QueueName=queue_name)

        return response["QueueUrl"]


async def get_sqs_message_count(queue_url: str):
    """
    SQS큐 메세지 개수 가져오기
    """
    async with await get_sqs_client() as client:
        response = await client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=[
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        )
        return ResGetWanSQSQueueCount(
            pending=int(response["Attributes"]["ApproximateNumberOfMessages"]),
            progress=int(
                response["Attributes"]["ApproximateNumberOfMessagesNotVisible"]
            ),
        )


async def receive_sqs_message(queue_url: str, wait_time: int = 5):
    """
    SQS큐 메시지 가져오기
    """
    async with await get_sqs_client() as client:
        response = await client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=wait_time,
            VisibilityTimeout=5,
        )

    return response.get("Messages", [])


async def delete_sqs_message(queue_url: str, receipt_handle: str):
    """
    SQS 메시지를 삭제합니다.
    """
    try:
        async with await get_sqs_client() as client:
            await client.delete_message(
                QueueUrl=queue_url, ReceiptHandle=receipt_handle
            )
        logger.info("메시지 삭제 완료")
    except Exception as e:
        logger.error(f"메시지 삭제 중 에러: {e}", exc_info=True)
        raise
