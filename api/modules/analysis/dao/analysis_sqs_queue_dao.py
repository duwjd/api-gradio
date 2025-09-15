import logging
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.mariadb.mariadb_config import AsyncSessionOp
from database.mariadb.models.resource_sqs_queue_model import ResourceSqsQueue

logger = logging.getLogger("app")


async def get_analysis_cunsumer_sqs_queues(db: AsyncSession):
    """
    SQS analysis cunsumer 처리 큐 조회
    """
    env = os.getenv("ENV")

    type = ResourceSqsQueue.type.like(f'%"request_api"%')
    query = select(ResourceSqsQueue).where(
        type,
        ResourceSqsQueue.env == env,
        ResourceSqsQueue.is_active == True,
    )
    result = await db.execute(query)
    rows = result.scalars().all()

    return [row.name for row in rows]


async def get_analysis_producer_sqs_queue():
    """
    SQS analysis producer 처리 큐 조회
    """
    env = os.getenv("ENV")

    async with AsyncSessionOp() as db:
        type = ResourceSqsQueue.type.like(f'%"response_api"%')
        query = select(ResourceSqsQueue).where(
            type,
            ResourceSqsQueue.env == env,
            ResourceSqsQueue.is_active == True,
        )
        result = await db.execute(query)
        row = result.scalars().first()

        return row.name
