from typing import Any, List, Literal, Optional, Union

from pydantic import Field

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


class TaskGradioSchema(BaseConfigModel):
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
    video_type: Optional[str] = None
    model: Optional[dict] = None
    type: Optional[str] = None      # 기존 호환성을 위해 유지
    value: Optional[str] = None     # 기존 호환성을 위해 유지


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
