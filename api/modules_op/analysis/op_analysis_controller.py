from typing import List, Optional, Union

from fastapi import APIRouter, Query, Response

from api.modules_op.analysis.op_analysis_service import OpAnalysisService
from api.modules_op.schema.op_analysis_schema import (
    ReqCreateAnalysisCode,
    ReqDeleteAnalysis,
    ReqDeployAnalysis,
    ReqGetAnalysisPendingProjectCount,
    ReqUpdateAnalysis,
    ResCreateAnalysisCode,
    ResGetAnalysisCodes,
)

op_analysis_api = APIRouter(prefix="/op", tags=["[관리 페이지] 분석코드 API"])


@op_analysis_api.post(
    "/analysis",
    summary="분석 코드 생성",
    response_model=ResCreateAnalysisCode,
    status_code=201,
)
async def op_create_analysis(req_body: ReqCreateAnalysisCode):
    """
    분석 코드 생성
    """
    return await OpAnalysisService.op_create_analysis(req_body)


@op_analysis_api.get(
    "/analysis",
    summary="분석 목록",
    response_model=Union[List[ResGetAnalysisCodes], List],
)
async def op_get_analysis(
    env: str = Query(None),
    type: Optional[str] = Query(None),
):
    """
    분석 목록
    - **env** 별로 조회합니다 (필수 입력)
    - **type**: 분석 타입별 목록 조회시
    ```
    env : op | development | staging | production
    type : 분석 타입
    ```
    """
    return await OpAnalysisService.op_get_analysis(env, type)


@op_analysis_api.put(
    "/analysis",
    summary="분석 수정",
    response_class=Response,
    response_model_exclude_none=True,
)
async def op_update_analysis(req_body: ReqUpdateAnalysis):
    """
    분석 수정
    """
    return await OpAnalysisService.op_update_analysis(req_body)


@op_analysis_api.delete(
    "/analysis",
    summary="분석 삭제",
    response_class=Response,
)
async def op_delete_analysis(req_body: ReqDeleteAnalysis):
    """
    분석 삭제
    """
    return await OpAnalysisService.op_delete_analysis(req_body)


@op_analysis_api.post(
    "/analysis/deploy",
    summary="분석 배포",
    response_class=Response,
)
async def op_deploy_analysis(req_body: ReqDeployAnalysis):
    """
    operation_ai DB에 있는 분석, 분석코드 테이블 env에 배포합니다.

    `env : development | staging | production`
    """
    return await OpAnalysisService.op_deploy_analysis(req_body)


@op_analysis_api.get(
    "/analysis/task_count",
    summary="분석 pending task 조회",
    response_model=list[ReqGetAnalysisPendingProjectCount],
)
async def op_get_analysis_task_count():
    """
    분석 pending task 조회

    ```
    env : development | staging | production
    pending_task_count: 대기 중인 SQS 큐 메시지 수 (비디오 생성 대기 메세지 수)
    pending_project_count: 현재 분석 중인 프로젝트 수 (사용자 요청의 progress 상태 건수)
    progress_task_count: 작업중인 SQS 큐 메시지 수 (비디오 생성 진행 수)
    ```
    """
    return await OpAnalysisService.op_get_analysis_task_count()
