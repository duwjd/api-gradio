import os

import redis

from database.redis.redis_config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_RETRY_ON_TIMEOUT,
    REDIS_SOCKET_TIMEOUT,
)


def redis_client():

    ENV = os.environ.get("ENV")

    # if ENV == "local":
    #     connection_class = redis.Connection
    # else:
    #     connection_class = redis.SSLConnection

    connection_class = redis.Connection
    # Redis 클라이언트 생성
    pool = redis.ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        socket_timeout=REDIS_SOCKET_TIMEOUT,
        retry_on_timeout=REDIS_RETRY_ON_TIMEOUT,
        decode_responses=True,
        max_connections=100,
        connection_class=connection_class,  # ✅ SSL 여부 적용
    )

    return redis.Redis(connection_pool=pool)


# 연결 테스트 (옵션)
def test_connection():
    try:
        redis_client.ping()
        print("Redis 연결 성공!")
    except redis.ConnectionError as e:
        print(f"Redis 연결 실패: {e}")


# 모듈이 직접 실행될 때 연결 테스트
if __name__ == "__main__":
    test_connection()
