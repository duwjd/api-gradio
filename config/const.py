import json
from enum import Enum
import os


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
    ANALYSIS_RESULT = "analysis.json"
    HTTPS = "https://cdn.gemgem.video/"


class STATUS_OK(str, BaseStrEnum):
    OK = "ok"


# API STATUS 정의
class STATUS(str, BaseStrEnum):
    INIT = "init"
    PENDING = "pending"
    PROGRESS = "progress"
    SUCCESS = "success"
    FAIL = "fail"


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
    # 분석 요청 큐
    GRADIO_ANALYSIS_REQUEST = "gradio_ai_analysis_request.fifo"
    LOCAL_ANALYSIS_REQUEST = "local_ai_analysis_request.fifo"
    DEV_ANALYSIS_REQUEST = "development_ai_analysis_request.fifo"
    STG_ANALYSIS_REQUEST = "staging_ai_analysis_request.fifo"
    PRD_ANALYSIS_REQUEST = "production_ai_analysis_request.fifo"

    # 분석 결과 큐
    GRADIO_ANALYSIS_RESPONSE = "gradio_ai_analysis_response.fifo"
    LOCAL_ANALYSIS_RESPONSE = "local_ai_analysis_response.fifo"
    DEV_ANALYSIS_RESPONSE = "development_ai_analysis_response.fifo"
    STG_ANALYSIS_RESPONSE = "staging_ai_analysis_response.fifo"
    PRD_ANALYSIS_RESPONSE = "production_ai_analysis_response.fifo"

    # 모델 분석 요청 큐
    GRADIO_WAN_2_1_REQUEST = "gradio_ai_wan2_1_request.fifo"
    GRADIO_WAN_2_2_REQUEST = "gradio_ai_wan2_2_request.fifo"
    LOCAL_WAN_REQUEST = "local_ai_wan_request.fifo"
    DEV_WAN_REQUEST = "development_ai_wan_request.fifo"
    STG_WAN_REQUEST = "staging_ai_wan_request.fifo"
    PRD_WAN_REQUEST = "production_ai_wan_request.fifo"

    # 모델 분석 결과 큐
    GRADIO_WAN_2_1_RESPONSE = "gradio_ai_wan2_1_response.fifo"
    GRADIO_WAN_2_2_RESPONSE = "gradio_ai_wan2_2_response.fifo"
    LOCAL_WAN_RESPONSE = "local_ai_wan_response.fifo"
    DEV_WAN_RESPONSE = "development_ai_wan_response.fifo"
    STG_WAN_RESPONSE = "staging_ai_wan_response.fifo"
    PRD_WAN_RESPONSE = "production_ai_wan_response.fifo"

    # master 분석 요청 큐
    GRADIO_MASTER_REQUEST = "gradio_ai_master_request.fifo"
    LOCAL_MASTER_REQUEST = "local_ai_master_request.fifo"
    DEV_MASTER_REQUEST = "development_ai_master_request.fifo"
    STG_MASTER_REQUEST = "staging_ai_master_request.fifo"
    PRD_MASTER_REQUEST = "production_ai_master_request.fifo"

    DOCUMENT_PARSER = "document_parser.fifo"
    MASK_IMAGE = "mask_image.fifo"
    INSERT_ANYTHING = "insert_anything.fifo"
    RELIGHT_IMAGE = "relight_image.fifo"
    FRAMEPACK = "framepack.fifo"
    LTX_DISTIL = "ltx_distil.fifo"
    WAN = "wan.fifo"


class SQS_QUEUE_COUNT:
    MAX_MASTER_CONSUMER_COUNT = 10
    MAX_ANALYSIS_CONSUMER_COUNT = 10
    MAX_ANALYSIS_PRODUCER_COUNT = 10


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
    WAN2_1 = ("ENGINE", "WAN", "2.1", "")
    WAN2_2 = ("ENGINE", "WAN", "2.2", "")
    KLING_V2_1 = ("API", "KLING", "2.1", "")
    SEEDANCE_1_LITE = ("API", "SEEDANCE", "1.0", "LITE")
    SEEDANCE_1_PRO = ("API", "SEEDANCE", "1.0", "PRO")

# 최대 이미지 개수
MAX_IMAGES = 4

# 분석 코드
I2V_ANALYSIS_CODE = ["AI-GRADIO-IMAGE2VIDEO-000001"]
I2I_ANALYSIS_CODE = ["AI-GRADIO-IMAGE2IMAGE-000001"]


# 영상 생성 모델 선택지들
VIDEO_MODELS = [
    "WAN2.1", 
    "WAN2.2", 
    "Kling2.1"
]

# 지원되는 이미지 파일 타입들
IMAGE_FILE_TYPES = [
    ".png", 
    ".jpg", 
    ".jpeg", 
    ".webp"
]

# 해상도 선택 옵션들
RESOLUTION_OPTIONS = [
    "480*720", 
    "720*1280"
]

# FPS 선택 옵션들
FPS_OPTIONS = [16, 24, 30]

# LoRA 선택 옵션들
LORA_OPTIONS = [
    "None", 
    "Wan21_CausVid_14B_T2V_lora_rank32.safetensors", 
    "Wan21_CausVid_14B_T2V_lora_rank32_v2.safetensors"
]

# 이미지 선택 옵션들
IMAGE_CHOICE_OPTIONS = ["image", "prompt"]

# WAN 모델 기본값들
WAN_DEFAULT_VALUES = {
    "resolution": "480*720",
    "fps": 24,
    "total_second_length": 2,
    "negative_prompt": "",
    "lora_selection" : "",
    "num_inference_steps": 20,
    "guidance_scale": 5.0,
    "shift": 5.0,
    "seed": 42
}

# Slider 설정값들
SLIDER_CONFIGS = {
    "total_second_length": {"min": 1, "max": 10, "step": 1},
    "num_inference_steps": {"min": 10, "max": 50, "step": 1},
    "guidance_scale": {"min": 1.0, "max": 20.0, "step": 0.1},
    "shift": {"min": 1.0, "max": 10.0, "step": 0.1}
}

# 앱 설명 마크다운
APP_DESCRIPTION = """
# gemgem-ai-api test
* 모든 프로젝트들은 userId=1, projectId=1로 고정됩니다.
"""

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

    AI_API_ANALYSIS_REPLICATE_UNATHENTICATED = (
        "AI_API_ANALYSIS_REPLICATE_UNATHENTICATED",
        "REPLICATE 인증에 실패했습니다.",
        500,
    )

    AI_API_ANALYSIS_REPLICATE_INVALID_TOKEN = (
        "AI_API_ANALYSIS_REPLICATE_INVALID_TOKEN",
        "REPLICATE 토큰이 유효하지 않습니다",
        500,
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

    AI_API_SQS_MESSAGE_SEND_FAIL = (
        "AI_API_SQS_SEND_FAIL",
        "SQS 메시지 전송에 실패했습니다.",
        500,
    )

    AI_API_SQS_MESSAGE_RECEIVE_FAIL = (
        "AI_API_SQS_MESSAGE_RECEIVE_FAIL",
        "SQS 메시지 조회에 실패했습니다.",
        500,
    )

    AI_API_SQS_MESSAGE_DELETE_FAIL = (
        "AI_API_SQS_MESSAGE_DELETE_FAIL",
        "SQS 메시지 삭제에 실패했습니다.",
        500,
    )

    AI_API_SQS_GET_URL_FAIL = (
        "AI_API_SQS_GET_URL_FAIL",
        "SQS 큐 URL 가져오기에 실패했습니다.",
        500,
    )

    AI_API_ASSIST_FAIL = (
        "AI_API_ASSIST_FAIL",
        "LLM 어시스트 요청에 실패했습니다.",
        500,
    )
