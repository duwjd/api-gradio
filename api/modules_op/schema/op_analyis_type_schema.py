from typing import Optional

from api.modules.schema import BaseConfigModel


class ReqCreateAnalysisType(BaseConfigModel):
    type: str


class ResGetAnalysisTypes(BaseConfigModel):
    type: str
    name: Optional[str] = None
    created_at: Optional[str]
    updated_at: Optional[str]


class ReqUpdateAnalysisType(BaseConfigModel):
    type: str
    name: str


class ReqDeleteAnalysisType(BaseConfigModel):
    type: str
