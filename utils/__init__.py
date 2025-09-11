from .s3_util import s3_client
from .gpt_util import gpt_client
from .google_util import vision_client, genai_client  # init_vertex_ai

import os


def register_clients():
    """
    모든 client 풀링 하는 형태로 구현

    client 등록 통합 함수(s3, gemini, ...)
    등록된 client 들은 gunicorn 실행 시 create_app에서 한번만 호출 (풀링 처리) -> 풀링 된 client 재사용 하여 api 호출
    """
    # s3_client()
    gpt_client()
    vision_client()
    genai_client()
    # init_vertex_ai()
