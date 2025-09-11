from pydantic import BaseModel, ConfigDict


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")  # 모든 모델에서 추가 필드 금지


class BaseQueryConfigModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
