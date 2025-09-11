import asyncio
import os
from typing import Optional

import vertexai
from fastapi import Request
from google import genai
from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorClient
from google.genai import types

# 전역 변수 (싱글톤 패턴 적용)
_vision_client: Optional[ImageAnnotatorClient] = None
_vertex_ai_initialized = False  # Vertex AI 초기화 여부


def _init_google_credentials():
    """
    Google Cloud 인증 환경 변수를 설정합니다.
    """
    credentials_file_path = (
        "../env/cat-product-426202-609db0569bcb.json"  # 실제 파일 경로로 변경
    )
    credentials_file_path = os.path.join(
        os.path.dirname(__file__), credentials_file_path
    )

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file_path


def vision_client():
    """
    Google Cloud Vision API 클라이언트를 생성합니다.

    Example:
        >>> client = get_vision_client()
        >>> type(client)
        <class 'google.cloud.vision_v1.ImageAnnotatorClient'>
    """
    global _vision_client
    if _vision_client is None:
        _init_google_credentials()
        _vision_client = vision.ImageAnnotatorClient()


def init_vertex_ai():
    """
    Vertex AI를 초기화합니다.

    Example:
        >>> init_vertex_ai()
    """
    global _vertex_ai_initialized
    if not _vertex_ai_initialized:
        _init_google_credentials()
        vertexai.init(project="cat-product-426202", location="asia-northeast3")
        _vertex_ai_initialized = True


def genai_client():

    return genai.Client(
        # Timeout for the request in milliseconds
        api_key=os.environ.get("GEMINI_API_KEY"),
        http_options={"timeout": 300000},
    )


def get_genai_client(request: Request):
    genai_client = request.app.state.genai_client
    if genai_client is None:
        raise RuntimeError("genai 클라이언트가 초기화 되지 않았습니다.")
    return genai_client


async def gemini_client_async():
    """
    비동기 gemini client 반환
    """
    return await asyncio.to_thread(genai_client)
