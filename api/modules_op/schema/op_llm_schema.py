from typing import Optional

from api.modules.schema import BaseConfigModel


class ResGetLLM(BaseConfigModel):
    code: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class ReqUpdateLLM(BaseConfigModel):
    code: str
    is_active: bool
    priority: int
