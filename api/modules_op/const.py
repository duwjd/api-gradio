from enum import Enum


class BaseStrEnum(Enum):
    """
    str 반환
    """

    def __str__(self):

        return self.value  # Enum 객체를 str로 변환


class BaseErrorEnum(Enum):
    """
    에러 예외처리 반환
    """

    def __init__(self, code: str, message: str, status_code: str):

        self.code = code
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        """code와 message를 딕셔너리 형태로 반환"""
        return {"code": self.code, "message": self.message}


class S3(str, BaseStrEnum):
    BUCKET = "cat-10k1m"
    PUBLIC_BUCKET = "gemgem-public-10k1m"
    PRIVATE_BUCKET = "gemgem-private-10k1m"
    REGION = "ap-northeast-2"
    IMAGE_PATH = "images/"
    GENERATOR_IMAGE_NAME = "generator_image"
    HTTPS = "https://cdn.gemgem.video/"


class STATUS_OK(str, BaseStrEnum):
    OK = "ok"


# API STATUS 정의
class STATUS(str, BaseStrEnum):
    INIT = "init"
    PROGRESS = "progress"
    SUCCESS = "success"
    FAIL = "fail"
    PENDING = "pending"


# MIME 타입 정의
class MimeType(str, BaseStrEnum):
    PDF = "application/pdf"
    PNG = "image/png"
    JPEG = "image/jpeg"


class DOCUMENT_TYPE(str, BaseStrEnum):
    FLYER = "flyer"
    DOCUMENT = "document"
    CARDNEWS = "cardnews"
    GG_PROJECT = "gg-project"
    GG_PROJECT_LEGACY = "gg-project-legacy"
    GG_URL = "gg-url"
    PAMPHLET = "pamphlet"


class GROUP(str, BaseStrEnum):
    SAMSUNG = "samsung.com"
    BODYFRIEND = "Bodyfriend.co.kr"
    DONGA = "donga.com"
    KT = "kt.com"
    GEMGEM = "gemgem.demo"
    TEST = "test"


class PROMPT_TYPE(str, BaseStrEnum):
    OCR = "OCR"


class TEST(str, BaseStrEnum):
    TEST = "test"


class LLM(int, BaseStrEnum):
    TIMEOUT = 120  # 2분


class LLM_CODE(str, BaseStrEnum):
    LLM_CHATGPT = "LLM-CHATGPT"
    LLM_GEMINI = "LLM-GEMINI"


class AI_MODEL(str, BaseStrEnum):
    LLM = "llm"
    DOCUMENT_PARSER = "document_parser"
    MASK_IMAGE = "mask_image"
    INSERT_ANYTHING = "insert_anything"
    RELIGHT_IMAGE = "relight_image"
    FRAMEPACK = "framepack"


class OP_ANALYSIS_ERROR(BaseErrorEnum):
    AI_OP_API_DATE_FORMAT_INVALID = (
        "AI_OP_API_DATE_FORMAT_INVALID",
        "날짜 형식은 (YYYY-MM-DD) 이어야 합니다",
        400,
    )

    AI_OP_API_PROMPT_CREATE_INVALID = (
        "AI_OP_API_PROMPT_CREATE_INVALID",
        "유효하지 않은 프롬프트 생성 요청입니다.",
        400,
    )

    AI_OP_API_PROMPT_UPDATE_INVALID = (
        "AI_OP_API_PROMPT_UPDATE_INVALID",
        "유효하지 않은 프롬프트 수정 요청입니다.",
        400,
    )

    AI_OP_API_PROMPT_DELETE_INVALID = (
        "AI_OP_API_PROMPT_DELETE_INVALID",
        "유효하지 않은 프롬프트 삭제 요청입니다.",
        400,
    )
