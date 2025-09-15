import logging
import os

from fastapi import APIRouter

from api.modules.swagger.common_doc import helath_check_doc, version_doc
from api.version_json import get_version_str
from config.const import STATUS, STATUS_OK

logger = logging.getLogger("app")

app_version: str = get_version_str(
    os.path.join(os.path.dirname(__file__), "../version.json"), format="display"
)


def master_register_router():
    """
    API 등록
    """
    api_router = APIRouter(prefix="/api")

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
