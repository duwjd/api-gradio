import logging
import os

from fastapi import APIRouter

from api.modules.swagger.common_doc import helath_check_doc, version_doc
from api.modules_op.analysis.op_analysis_controller import op_analysis_api
from api.modules_op.analysis_type.op_analysis_type_controller import (
    op_analysis_type_api,
)
from api.modules_op.llm.op_llm_controller import op_llm_api
from api.modules_op.music.op_music_controller import op_music_api
from api.modules_op.prompt.op_prompt_controller import op_prompt_api
from api.modules_op.task.op_task_controller import op_task_api
from api.version_json import get_version_str
from config.const import STATUS, STATUS_OK

logger = logging.getLogger("app")

app_version: str = get_version_str(
    os.path.join(os.path.dirname(__file__), "../version.json"), format="display"
)


def op_api_register_router():
    """
    API 등록
    """
    api_router = APIRouter(prefix="/api")

    # controller API 등록
    api_router.include_router(common_api)
    api_router.include_router(op_analysis_api)
    api_router.include_router(op_analysis_type_api)
    api_router.include_router(op_music_api)
    api_router.include_router(op_llm_api)
    api_router.include_router(op_task_api)
    api_router.include_router(op_prompt_api)

    return api_router


common_api = APIRouter(prefix="", tags=["Common"])


@common_api.get("/version", responses=version_doc())
async def version():

    return {
        "status": STATUS.SUCCESS,
        "version": app_version,
    }


@common_api.get("/healthcheck", responses=helath_check_doc())
async def health_check():
    return {"status": STATUS_OK.OK}
