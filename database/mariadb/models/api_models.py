from sqlalchemy import MetaData

from database.mariadb.models import Base
from database.mariadb.models.resource_ai_model_model import ResourceAiModel
from database.mariadb.models.resource_analysis_model import ResourceAnalysis
from database.mariadb.models.resource_analysis_type_model import ResourceAnalysisType
from database.mariadb.models.resource_llm_model import ResourceLLM
from database.mariadb.models.resource_music_keyword_model import ResourceMusicKeyword
from database.mariadb.models.resource_music_model import ResourceMusic
from database.mariadb.models.resource_music_weight_model import ResourceMusicWeight
from database.mariadb.models.resource_prompt_model import ResourcePrompt
from database.mariadb.models.resource_ref_image_modle import ResourceRefImage
from database.mariadb.models.resource_vessl_model import ResourceVessl
from database.mariadb.models.resource_video_model import ResourceVideoModel
from database.mariadb.models.task_engine_model import TaskEngine
from database.mariadb.models.task_llm_model import TaskLLM


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


class ApiModels:
    MODELS = [
        ResourceAnalysis,
        ResourceAnalysisType,
        ResourceMusic,
        ResourceMusicKeyword,
        ResourceMusicWeight,
        ResourceLLM,
        ResourcePrompt,
        ResourceVessl,
        ResourceAiModel,
        ResourceRefImage,
        ResourceVideoModel,
        TaskEngine,
        TaskLLM,
    ]

    @classmethod
    def get_metadata(cls) -> MetaData:
        return extract_metadata_for(cls.MODELS)
