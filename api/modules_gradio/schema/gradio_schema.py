from typing import Any, List, Literal, Optional, Union

from api.modules.schema import BaseConfigModel
from config.const import STATUS, STATUS_OK

from pydantic import BaseModel, ConfigDict, Field
from PIL import Image

class BaseAiInputSchema(BaseModel):
    """
    Base schema for AI model input.
    """

    model_config = ConfigDict(
        extra="forbid",  # 모든 모델에서 추가 필드 금지
        arbitrary_types_allowed=True,  # 임의의 타입 허용
    )

class Wan2VideoInputSchema(BaseAiInputSchema):
    image: Optional[Image.Image] = Field(default=None)
    prompt: str = Field(default="")
    negative_prompt: str = Field(default="")
    total_second_length: int = Field(default=5, ge=1, le=10)
    frames_per_second: int = Field(default=24, ge=1, le=60)
    num_inference_steps: int = Field(default=50, ge=2, le=100)
    guidance_scale: float = Field(default=5.0, ge=1.0, le=10)
    shift: float = Field(default=5.0, ge=1.0, le=10.0)
    # constants
    sample_solver: str = Field(default="unipc")
    offload_model: bool = Field(default=True)
    target_h: int = Field(default=1280)
    target_w: int = Field(default=720)
    seed: int = Field(default=42, ge=0, le=2**32 - 1)
    upload_folder: str = Field(default="")

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


class DoAnalysisOption(BaseConfigModel):
    src: str
    type: Literal["image", "prompt", "filter"] = Field(
        ..., description="허용된 타입만 가능"
    )
    value: str


class ReqDoAnalysis(BaseConfigModel):
    userId: int
    projectId: int
    documentS3: Optional[Union[List[str], str, List[dict]]] = None
    analysisS3: Optional[str] = None
    analysisHttps: Optional[str] = None
    group: Optional[str] = None
    type: str
    option: list[DoAnalysisOption] = None
    templateCode: Optional[str] = None
    chunkData: Optional[List[Any]] = Field(default_factory=list)
    pages: Optional[List[int]] = Field(default_factory=list)
    prompt: Optional[List[Any]] = None
    inputUrl: Optional[str] = None
    inputData: Optional[str] = None
    test: Optional[dict] = None


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
