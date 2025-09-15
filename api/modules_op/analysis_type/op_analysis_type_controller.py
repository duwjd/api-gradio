from typing import List, Union

from fastapi import APIRouter, Response

from api.modules_op.analysis_type.op_analysis_type_service import OpAnalysisTypeService
from api.modules_op.schema.op_analyis_type_schema import (
    ReqCreateAnalysisType,
    ReqDeleteAnalysisType,
    ReqUpdateAnalysisType,
    ResGetAnalysisTypes,
)

op_analysis_type_api = APIRouter(prefix="/op", tags=["[관리 페이지] 분석타입 API"])


@op_analysis_type_api.post(
    "/analysis/type",
    summary="분석 타입 생성",
    response_class=Response,
    status_code=201,
)
async def op_create_analysis_type(req_body: ReqCreateAnalysisType):
    """
    분석 타입 생성
    """
    return await OpAnalysisTypeService.op_create_analysis_type(req_body)


@op_analysis_type_api.get(
    "/analysis/type",
    summary="분석 타입 목록",
    response_model=Union[List[ResGetAnalysisTypes], List],
)
async def op_get_analysis_types():
    """
    분석 타입 목록
    """
    return await OpAnalysisTypeService.op_get_analysis_types()


@op_analysis_type_api.put(
    "/analysis/type", summary="분석 타입 수정", response_class=Response
)
async def op_update_analysis_type(req_body: ReqUpdateAnalysisType):
    """
    분석 타입 수정
    """
    return await OpAnalysisTypeService.op_update_analysis_type(req_body)


@op_analysis_type_api.delete(
    "/analysis/type", summary="분석 타입 삭제", response_class=Response
)
async def op_delete_analysis_type(req_body: ReqDeleteAnalysisType):
    """
    분석 타입 삭제
    """
    return await OpAnalysisTypeService.op_delete_analysis_type(req_body)
