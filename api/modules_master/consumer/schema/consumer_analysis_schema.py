from api.modules.schema import BaseConfigModel


class ReqConsumerAnalysis(BaseConfigModel):
    status: str
    userId: int
    projectId: int
    analysisCode: str
    errorCode: str
    errorMessage: str
