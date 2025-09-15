from datetime import datetime
from typing import Optional

from pydantic import Field

from api.modules.schema import BaseConfigModel, BaseQueryConfigModel
from config.const import STATUS


class ReqOpGetTaskPagenation(BaseConfigModel):
    env: str
    page: Optional[int] = None
    size: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class ResOpGetTaskList(BaseConfigModel):
    id: int
    user_id: int
    project_id: int
    analysis_code: str
    analysis_type: str
    status: STATUS
    progress: int = None
    request_body: Optional[str] = None
    llm_result: Optional[str] = None
    result: Optional[str] = None
    end_at: Optional[float]
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime] = None


class ReqOpGetTaskPagenation(BaseQueryConfigModel):
    env: str
    user_id: Optional[int] = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1)
    start_date: Optional[str] = Field("2025-01-01 00:00:00")
    end_date: Optional[str] = Field("2025-12-31 23:59:59")
    status: Optional[str] = None
    analysis_type: Optional[str] = Field(None, alias="analysis_type")


class ResOpGetTaskPagenation(BaseConfigModel):
    total_count: int
    total_page: int
    list: list[ResOpGetTaskList]
