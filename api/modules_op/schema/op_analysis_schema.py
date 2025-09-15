from typing import List, Optional

from api.modules.schema import BaseConfigModel


class ReqCreateAnalysisCode(BaseConfigModel):
    type: str


class ResCreateAnalysisCode(BaseConfigModel):
    code: str


class ReqUpdateAnalysis(BaseConfigModel):
    code: str
    group: Optional[list] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ReqDeleteAnalysis(BaseConfigModel):
    code: str


class ReqDeployAnalysis(BaseConfigModel):
    env: str


class ResGetAnalysisCodes(BaseConfigModel):
    code: str
    type: Optional[str]
    group: List[str] = None
    name: Optional[str] = None
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class ReqGetAnalysisPendingProjectCount(BaseConfigModel):
    env: str
    pending_task_count: int
    pending_project_count: int
    progress_project_count: int
    progress_task_count: int
