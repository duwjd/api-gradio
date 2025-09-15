import boto3
import redis
import os
import hmac
import hashlib
import base64
import time
from urllib.parse import quote_plus

# Redis 서버 설정
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# 추가 설정 (옵션)
REDIS_SOCKET_TIMEOUT = int(
    os.environ.get("REDIS_SOCKET_TIMEOUT", 5)
)  # 기본 타임아웃 5초
REDIS_RETRY_ON_TIMEOUT = (
    os.environ.get("REDIS_RETRY_ON_TIMEOUT", "True").lower() == "true"
)
