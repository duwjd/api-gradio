from typing import Optional, Union

from api.modules.schema import BaseConfigModel, BaseQueryConfigModel


class ReqOpCreatePrompt(BaseConfigModel):
    analysis_code: str


class ReqOpGetPrompt(BaseQueryConfigModel):
    env: str
    llm_code: str
    group: str
    analysis_code: str


class ResOpGetPrompt(BaseConfigModel):
    prompt: Optional[Union[dict, str]] = None


class ResOpGetPromptGroup(BaseConfigModel):
    group: str
    analysis_code: list


class ReqOpUpdatePrompt(BaseConfigModel):
    llm_code: str
    group: str
    analysis_code: str
    prompt: str


class ReqOpDeletePrompt(BaseConfigModel):
    analysis_code: str


class ReqOpDeployPrompt(BaseConfigModel):
    env: str
