from openai import OpenAI
import os
from typing import Optional
from fastapi import Request


def get_gpt_client(request: Request):
    gpt_client = request.app.state.gpt_client
    if gpt_client is None:
        raise RuntimeError("OPENAI 클라이언트가 초기화되지 않았습니다.")
    return gpt_client


def gpt_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # 정상 동작
