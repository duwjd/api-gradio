import json
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
        """딕셔너리 형태로 반환"""
        return {"code": self.code, "message": self.message}


class BaseModelEnum(Enum):
    """
    모델 정의
    """

    def __init__(self, type: str, model_name: str, version: str, edition: str):

        self.type = type
        self.model_name = model_name
        self.version = version
        self.edition = edition

    def to_dict(self):
        return {
            "type": self.type,
            "model_name": self.model_name,
            "version": self.version,
            "edition": self.edition,
        }

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(
            {
                "type": self.type,
                "model_name": self.model_name,
                "version": self.version,
                "edition": self.edition,
            },
            ensure_ascii=False,
        )


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
    JPG = "image/jpg"
    WEBP = "image/webp"
    MPO = "image/jpeg"


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
    WAN = "wan"


class SQS_QUEUE(str, BaseStrEnum):
    DOCUMENT_PARSER = "document_parser.fifo"
    MASK_IMAGE = "mask_image.fifo"
    INSERT_ANYTHING = "insert_anything.fifo"
    RELIGHT_IMAGE = "relight_image.fifo"
    FRAMEPACK = "framepack.fifo"
    LTX_DISTIL = "ltx_distil.fifo"
    WAN = "wan.fifo"


class API_VIDEO_MODEL(str, BaseStrEnum):
    KLING_V2_1 = "kwaivgi/kling-v2.1"
    HAILUO_02 = "minimax/hailuo-02"
    SEEDANCE_1_LITE = "bytedance/seedance-1-lite"
    SEEDANCE_1_PRO = "bytedance/seedance-1-pro"


class API_MUSIC_MODEL(str, BaseStrEnum):
    ACE_STEP = "lucataco/ace-step:280fc4f9ee507577f880a167f639c02622421d8fecf492454320311217b688f1"
    MUSICGEN = (
        "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb"
    )


class MODEL(BaseModelEnum):
    WAN2_2 = ("ENGINE", "WAN", "2.2", "")
    KLING_V2_1 = ("API", "KLING", "2.1", "")
    SEEDANCE_1_LITE = ("API", "SEEDANCE", "1.0", "LITE")
    SEEDANCE_1_PRO = ("API", "SEEDANCE", "1.0", "PRO")


class ANALYSIS_ERROR(BaseErrorEnum):
    AI_API_ANALYSIS_REQUEST_INVALID = (
        "AI_API_ANALYSIS_REQUEST_INVALID",
        "잘못된 분석 요청 입니다.",
        400,
    )
    AI_API_MUSIC_ID_NOT_EXIST = (
        "AI_API_MUSIC_ID_NOT_EXIST",
        "존재하지 않는 음악 id입니다.",
        400,
    )
    AI_API_ANALYSIS_IS_RUNNING = (
        "AI_API_ANALYSIS_IS_RUNNING",
        "분석이 진행 중입니다.",
        422,
    )
    AI_API_ANALYSIS_REQUEST_FAIL = (
        "AI_API_ANALYSIS_REQUEST_FAIL",
        "분석 요청에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_RESPONSE_FAIL = (
        "AI_API_ANALYSIS_RESPONSE_FAIL",
        "분석 조회에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_TYPE_EXIST = (
        "AI_API_ANALYSIS_TYPE_EXIST",
        "존재하는 분석 타입입니다.",
        422,
    )

    AI_API_ANALYSIS_TYPE_INVALID = (
        "AI_API_ANALYSIS_TYPE_INVALID",
        "잘못된 분석 타입입니다.",
        422,
    )

    AI_API_ANALYSIS_CODE_NOT_EXIST = (
        "AI_API_ANALYSIS_CODE_NOT_EXIST",
        "지원하지 하지 않는 분석 코드입니다.",
        422,
    )
    AI_API_ENV_NOT_EXIST = (
        "AI_API_ENV_NOT_EXIST",
        "존재하지 않는 ENV 입니다. [op, development, staging, production]",
        422,
    )

    AI_API_STATUS_NOT_EXIST = (
        "AI_API_STATUS_NOT_EXIST",
        "존재하지 않는 STATUS 입니다. STATUS 종류 : (INIT, PROGRESS, SUCCESS, FAIL, PENDING)",
        422,
    )

    AI_API_ANALYSIS_TYPE_NOT_EXIST = (
        "AI_API_ANALYSIS_TYPE_NOT_EXIST",
        "존재하지 않는 분석 타입입니다.",
        422,
    )

    AI_API_ANALYSIS_NOT_REQUEST = (
        "AI_API_ANALYSIS_NOT_REQUEST",
        "요청된 분석이 없습니다. 분석을 요청 해주세요.",
        400,
    )
    AI_API_ANALYSIS_FAIL = ("AI_API_ANALYSIS_FAIL", "분석에 실패하였습니다.", 500)

    AI_API_INVALID_MIME_TYPE = (
        "AI_API_INVALID_MIME_TYPE",
        "지원하지 않는 파일 형식입니다.",
        422,
    )

    AI_API_INVALID_CAR_INPUT_FILE = (
        "AI_API_INVALID_INPUT_FILE",
        "유효하지 않은 입력 파일입니다. 자동차 사진을 업로드 해주세요.",
        422,
    )

    AI_API_GROUP_INVALID = (
        "AI_API_GROUP_INVALID",
        "잘못된 그룹 요청입니다.",
        422,
    )

    AI_API_LLM_PRIORITY_DUPLICATE = (
        "AI_API_LLM_PRIORITY_DUPLICATE",
        "LLM 우선순위가 중복 됐습니다.",
        422,
    )

    AI_API_ANALYSIS_MODEL_IS_RUNNING = (
        "AI_API_ANALYSIS_MODEL_IS_RUNNING",
        "모델 분석이 이미 진행 중입니다.",
        422,
    )

    AI_API_ANALYSIS_VALIDATE_FAIL = (
        "AI_API_ANALYSIS_VALIDATE_FAIL",
        "분석 결과가 json 형태가 아닙니다.",
        500,
    )

    AI_API_ANALYSIS_MATCH_FAIL = (
        "AI_API_ANALYSIS_MATCH_FAIL",
        "분석 결과가 템플릿 구조와 일치하지 않습니다.",
        500,
    )
    AI_API_FILE_DOWNLOAD_FAIL = (
        "AI_API_FILE_DOWNLOAD_FAIL",
        "파일 다운로드에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_VIDEO_API_FAIL = (
        "AI_API_ANALYSIS_VIDEO_API_FAIL",
        "API 비디오 생성에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_VIDEO_API_TIMEOUT = (
        "AI_API_ANALYSIS_VIDEO_API_TIMEOUT",
        "API 비디오 생성 타임아웃 시간 초과했습니다.",
        200,
    )

    AI_API_ANALYSIS_VIDEO_MODEL_INVALID = (
        "AI_API_ANALYSIS_VIDEO_MODEL_INVALID",
        "잘못된 비디오 모델 API 요청입니다.",
        500,
    )

    AI_API_ANALYSIS_PHOTO2VIDEO_REQUEST_NOT_EXIST = (
        "AI_API_ANALYSIS_PHOTO2VIDEO_REQUEST_NOT_EXIST",
        "생성된 초기 비디오가 존재하지 않습니다. 신규 생성 요청을 진행해주세요.",
        422,
    )

    AI_API_ANALYSIS_MUSIC_MODEL_INVALID = (
        "AI_API_ANALYSIS_MUSIC_MODEL_INVALID",
        "잘못된 음악 모델 API 요청입니다.",
        500,
    )

    AI_API_ANALYSIS_OPTION_NOT_EXIST = (
        "AI_API_ANALYSIS_OPTION_NOT_EXIST",
        "option 필드가 존재하지 않습니다.",
        400,
    )

    AI_API_ANALYSIS_VIDEO_MODEL_FAIL = (
        "AI_API_ANALYSIS_VIDEO_MODEL_FAIL",
        "모델 비디오 생성에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_VIDEO_MODEL_TIMEOUT = (
        "AI_API_ANALYSIS_VIDEO_MODEL_TIMEOUT",
        "모델 비디오 생성 타임아웃 시간 초과했습니다.",
        200,
    )

    AI_API_ANALYSIS_SENSITIVE_IMAGE = (
        "AI_API_ANALYSIS_SENSITIVE_IMAGE",
        "이미지에 민감한 정보가 감지되어 비디오 생성에 실패하였습니다.",
        422,
    )

    AI_API_ANALYSIS_SEXUAL_IMAGE = (
        "AI_API_ANALYSIS_SEXUAL_IMAGE",
        "이미지에 성적인 정보가 감지되어 비디오 생성에 실패하였습니다.",
        422,
    )

    AI_API_ANALYSIS_LLM_NOT_EXIST = (
        "AI_API_ANALYSIS_LLM_NOT_EXIST",
        "LLM 코드가 존재하지 않습니다.",
        500,
    )

    AI_API_ANALYSIS_PROMPT_NOT_EXIST = (
        "AI_API_ANALYSIS_PROMPT_NOT_EXIST",
        "prompt가 존재하지 않습니다.",
        500,
    )

    AI_API_ANALYSIS_INVALID_PIXEL_IMAGE = (
        "AI_API_ANALYSIS_INVALID_PIXEL_IMAGE",
        "이미지가 너무 작거나 커서 비디오 생성에 실패하였습니다.",
        422,
    )

    AI_API_ANALYSIS_INVALID_CROPPED_PIXEL_IMAGE = (
        "AI_API_ANALYSIS_INVALID_CROPPED_PIXEL_IMAGE",
        "자르기 후 이미지 크기가 너무 작거나 커서 비디오 생성에 실패하였습니다.",
        422,
    )

    AI_API_ANALYSIS_LLM_POLICY_VIOLATION_IMAGE = (
        "AI_API_ANALYSIS_LLM_POLICY_VIOLATION_IMAGE",
        "정책을 위반하는 이미지를 업로드하여 LLM이 답변을 거부했습니다.",
        422,
    )

    AI_API_ANALYSIS_LLM_POLICY_VIOLATION_PROMPT = (
        "AI_API_ANALYSIS_LLM_POLICY_VIOLATION_PROMPT",
        "정책을 위반하는 프롬프트를 입력하여 LLM이 답변을 거부했습니다.",
        422,
    )

    AI_API_ANALYSIS_LLM_RETRY_LIMIT_EXCEEDED = (
        "AI_API_ANALYSIS_LLM_RETRY_LIMIT_EXCEEDED",
        "LLM 최대 재시도 횟수에 도달했습니다.",
        422,
    )

    AI_API_ANALYSIS_REPLICATE_RETRY_LIMIT_EXCEEDED = (
        "AI_API_ANALYSIS_REPLICATE_RETRY_LIMIT_EXCEEDED",
        "REPLICATE 최대 재시도 횟수에 도달했습니다.",
        422,
    )

    AI_API_ANALYSIS_LOCATION_EXTRACTION_FAIL = (
        "AI_API_ANALYSIS_LOCATION_EXTRACTION_FAIL",
        "위치 정보 추출에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_IMAGE_PREPROCESS_FAIL = (
        "AI_API_ANALYSIS_IMAGE_PREPROCESS_FAIL",
        "이미지 전처리에 실패했습니다.",
        500,
    )
