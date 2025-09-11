import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Query, Request, Response

from api.modules.analysis.analysis_service import AnalysisService
from api.modules.analysis.schema.analysis_schema import (
    ReqDoAnalysis,
    ResDoAnalysis,
    ResGetAnalysis,
    ResGetWanSQSQueueCount,
)
from api.modules.swagger.analysis_doc import do_analysis_doc, get_analysis_doc

logger = logging.getLogger("app")

analysis_api = APIRouter(prefix="/analysis", tags=["Analysis"])


@analysis_api.post(
    "/document",
    summary="분석 요청",
    status_code=201,
    responses=do_analysis_doc(),
    response_model=ResDoAnalysis,
    response_model_exclude_none=True,
)
async def do_analysis(req_body: ReqDoAnalysis, background_tasks: BackgroundTasks):
    """
    llm 분석을 요청 합니다.
    """

    return await AnalysisService.do_analysis(req_body, background_tasks)


@analysis_api.get(
    "/document/{user_id}/{project_id}",
    summary="분석 조회",
    responses=get_analysis_doc(),
    response_model=ResGetAnalysis,
    response_model_exclude_none=True,
)
async def get_analysis(
    user_id: int,
    project_id: int,
    type: Optional[str] = Query(None),
    req_app: Request = None,
):
    """
    llm 분석 상태를 조회합니다.
    """

    return await AnalysisService.get_analysis(user_id, project_id, type, req_app)


@analysis_api.post(
    "/debug-sync",
    summary="analysis 테이블 싱크",
    response_model=None,
    response_class=Response,
)
async def sync_resource_analysis():
    """
    resource_analysis 테이블 싱크 업데이트 (dev -> local)
    """

    return await AnalysisService.sync_resource_analysis()
