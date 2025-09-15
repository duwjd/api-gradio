import logging
import json
from typing import Optional
from config.const import STATUS


logger = logging.getLogger("app")


def get_status_by_progress(progress: int) -> STATUS:
    """
    Progress 값에 따라 상태를 반환.

    Args:
        progress (int): Progress 값

    Returns:
        STATUS: 분석 상태 (SUCCESS, FAIL, PROGRESS)
    """
    if progress < 0:
        return STATUS.FAIL
    if progress < 100:
        return STATUS.PROGRESS
    if progress == 100:
        return STATUS.SUCCESS
    raise ValueError("Progress must be between -1 and 100.")


def update_redis_status(
    redis_client,
    key: str,
    progress: int,
    message: Optional[str] = None,
    doc_type: Optional[str] = None,
    ttl: int = 120,
) -> None:
    """Redis 상태를 progress에 따라 업데이트."""
    status = get_status_by_progress(progress)

    data = {
        "status": str(status),
        "progress": progress,
        **({"message": message} if message else {}),
        **({"type": doc_type} if doc_type else {}),
    }

    redis_client.set(key, json.dumps(data), ex=ttl)


def get_redis_status(redis_client, redis_key) -> STATUS:
    """
    redis 상태 조회

    Args:
        redis_client: redis client
        redis_key: redis key

    Returns:
        STATUS: 분석 상태 (SUCCESS, FAIL, PROGRESS, PENDING)
    """
    try:
        redis_json = redis_client.get(redis_key)
        if redis_json is None:
            return STATUS.PENDING

        redis_data = json.loads(redis_json)
        status: STATUS = redis_data.get("status")

        return status

    except Exception as e:
        logger.error(f"redis data get error: {e}")
