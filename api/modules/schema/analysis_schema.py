from typing import Any, List, Literal, Optional, Union
from PIL import Image
from pydantic import ConfigDict, Field, BaseModel

from api.modules.schema import BaseConfigModel
from config.const import STATUS, STATUS_OK


class TaskLLMSchema(BaseConfigModel):
    id: int
    user_id: int
    project_id: int
    analysis_code: str
    analysis_type: str
    status: STATUS
    progress: int = None
    result: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ResOk(BaseConfigModel):
    status: STATUS_OK = STATUS_OK.OK



class ModelOption(BaseModel):
    frames_per_second: int = Field(default=16, ge=1, le=60, alias="framesPerSecond")
    guidance_scale: float = Field(default=1.0, ge=1.0, le=10, alias="guidanceScale")
    image: Optional[Image.Image] = Field(default=None)
    max_area: int = Field(
        default=720 * 1280,
        alias="maxArea",  # 480 * 832 for 480p, 720 * 1280 for 720p
    )
    negative_prompt: str = Field(
        default=(
            "Bright tones, overexposed, static,"
            " blurred details, subtitles, style, works, paintings,"
            " images, static, overall gray, worst quality, low quality,"
            " JPEG compression residue, ugly, incomplete, extra fingers,"
            " poorly drawn hands, poorly drawn faces, deformed, disfigured,"
            " misshapen limbs, fused fingers, still picture, messy background,"
            " three legs, many people in the background, walking backwards, shaking"
        ),
        alias="negativePrompt",
    )
    num_inference_steps: int = Field(default=8, ge=8, le=50, alias="numInferenceSteps")
    prompt: str = Field(
        default=(
            "A sleek modern car driving slowly and smoothly forward, "
            "with a cinematic presentation style. The camera follows "
            "the car at a steady pace, showcasing its elegant design "
            "and motion. The car moves at a moderate speed"
        ),
        alias="prompt",
    )
    seed: int = Field(default=0, ge=0, le=2**32 - 1, alias="seed")
    shift: int = Field(default=8.0, ge=1.0, le=10.0, alias="shift")  # not used
    total_second_length: int = Field(default=5, ge=1, le=10, alias="totalSecondLength")
    lora_name: Optional[str] = Field(default="kijai_comfy_v1", alias="loraName")
    filter_name: Optional[str] = Field(default="empty", alias="filterName")
    # Configuration that allows PIL image object
    model_config = ConfigDict(
        extra="forbid",  # 모든 모델에서 추가 필드 금지
        arbitrary_types_allowed=True,  # 임의의 타입 허용
    )


class VideoModel(BaseModel):
    name: str = Field(..., description="모델 이름 (예: 'Wan2.2')")
    option: ModelOption = Field(..., description="모델 옵션 설정")

class VideoGenerationOption(BaseModel):
    src: str = Field(..., description="소스 파일 경로 (S3 URL 등)")
    video_type: str = Field(..., description="비디오 타입 ('API or ENGINE')")
    model: VideoModel = Field(..., description="사용할 모델과 설정")

class VideoGenerationRequest(BaseModel):
    option: List[VideoGenerationOption] = Field(..., description="비디오 생성 옵션 리스트")


class ReqDoAnalysis(BaseConfigModel):
    userId: int
    projectId: int
    documentS3: Optional[Union[List[str], str, List[dict]]] = None
    analysisS3: Optional[str] = None
    analysisHttps: Optional[str] = None
    group: Optional[str] = None
    type: str
    option: Optional[List[VideoGenerationOption]] = None


class ResDoAnalysis(BaseConfigModel):
    status: STATUS
    code: Optional[str] = None
    message: Optional[str] = None
    documentS3: Optional[list] = None


class ResGetAnalysis(BaseConfigModel):
    status: STATUS
    progress: Optional[int] = None
    type: Optional[str] = None
    code: Optional[str] = None
    message: Optional[str] = None
    result: Optional[Union[List[Any], dict]] = None


class ResGetAnalysisCodes(BaseConfigModel):
    code: str
    type: str
    role: List[str] = None
    group: List[str]
    name: str
    task_type: str = None
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class ResGetAnalysisTypes(BaseConfigModel):
    type: str
    name: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ResGetWanSQSQueueCount(BaseConfigModel):
    pending: int
    progress: int
