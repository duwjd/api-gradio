from typing import Any, List, Literal, Optional, Union

from pydantic import Field, BaseModel

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
    prompt: Optional[str] = Field(None, description="생성할 비디오에 대한 프롬프트")
    resolution: Optional[str] = Field(default="720*480", description="해상도")
    aspect_ratio: Optional[str] = Field(default="9:16", description="화면 비율등)")
    negative_prompt: Optional[str] = Field(default="", description="네거티브 프롬프트")
    total_second_length: Optional[int] = Field(default=5, description="총 비디오 길이 (초)")
    frames_per_second: Optional[int] = Field(default=24, description="초당 프레임 수")
    num_inference_steps: Optional[int] = Field(None, description="추론 단계 수")
    guidance_scale: Optional[float] = Field(None, description="가이던스 스케일")
    shift: Optional[float] = Field(None, description="시프트 값")
    seed: Optional[int] = Field(None, description="시드 값")

class VideoModel(BaseModel):
    name: str = Field(..., description="모델 이름 (예: 'Wan2.2')")
    option: ModelOption = Field(..., description="모델 옵션 설정")

class VideoGenerationOption(BaseModel):
    src: str = Field(..., description="소스 파일 경로 (S3 URL 등)")
    video_type: str = Field(..., description="비디오 타입 (예: 'API or ENGINE')")
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
