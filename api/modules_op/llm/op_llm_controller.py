from typing import List, Union

from fastapi import APIRouter, Query, Response

from api.modules_op.llm.op_llm_service import OpLLMService
from api.modules_op.schema.op_llm_schema import ReqUpdateLLM, ResGetLLM

op_llm_api = APIRouter(prefix="/op", tags=["[관리 페이지] LLM API"])


@op_llm_api.get(
    "/llm",
    response_model=Union[List[ResGetLLM], List],
    summary="LLM 목록 조회",
)
async def op_get_llms():
    """
    LLM 목록 조회
    """
    return await OpLLMService.op_get_llms()


@op_llm_api.put(
    "/llm",
    summary="LLM 수정",
    response_class=Response,
)
async def op_update_llm(req_body: List[ReqUpdateLLM]):
    """
    LLM 수정
    """
    return await OpLLMService.op_update_llm(req_body)
