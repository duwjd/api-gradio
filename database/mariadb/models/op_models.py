from sqlalchemy import MetaData

from database.mariadb.models import Base
from database.mariadb.models.resource_analysis_model import ResourceAnalysis
from database.mariadb.models.resource_analysis_type_model import ResourceAnalysisType
from database.mariadb.models.resource_music_keyword_model import ResourceMusicKeyword
from database.mariadb.models.resource_music_model import ResourceMusic
from database.mariadb.models.resource_music_weight_model import ResourceMusicWeight
from database.mariadb.models.resource_llm_model import ResourceLLM
from database.mariadb.models.resource_prompt_model import ResourcePrompt
from database.mariadb.models.resource_sqs_queue_model import ResourceSqsQueue
from database.mariadb.models.resource_worker_model import ResourceWorker
from database.mariadb.models.resource_ai_model_model import ResourceAiModel


def extract_metadata_for(models: list[type], base_metadata=Base.metadata) -> MetaData:
    """
    Base.metadata에 등록된 테이블 중에서
    지정된 모델만 새 MetaData에 복사
    """
    metadata = MetaData()
    for model in models:
        table = model.__table__
        if table.name in base_metadata.tables:
            table.tometadata(metadata)
    return metadata


class OpModels:
    MODELS = [
        ResourceAnalysis,
        ResourceAnalysisType,
        ResourceMusic,
        ResourceMusicKeyword,
        ResourceMusicWeight,
        ResourceLLM,
        ResourcePrompt,
        ResourceSqsQueue,
        ResourceWorker,
        ResourceAiModel,
    ]

    @classmethod
    def get_metadata(cls) -> MetaData:
        return extract_metadata_for(cls.MODELS)
