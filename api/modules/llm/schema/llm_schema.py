from typing import Any, Optional, Union

from api.modules.schema import BaseConfigModel


class ReqDoLLM(BaseConfigModel):
    userId: int
    projectId: int
    analysisCode: str
    type: str
    inputData: Union[str, list]
    prompt: Union[str, dict]
    systemPrompt: Optional[str] = None
    startProgress: int
    endProgress: int


class ResGetLLMS(BaseConfigModel):
    code: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class ResGetLLM(BaseConfigModel):
    result: list[Any]


class ReqDoUpstageOCR(BaseConfigModel):
    inputData: str


class ReqLLMAssist(BaseConfigModel):
    userId: int
    projectId: int
    type: str
    inputData: str
