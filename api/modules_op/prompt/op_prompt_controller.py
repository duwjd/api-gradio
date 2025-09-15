from typing import Annotated, List, Optional, Union

from fastapi import APIRouter, Depends, Query, Response

from api.modules_op.prompt.op_prompt_service import OpPromptService
from api.modules_op.prompt.scema.op_prompt_schema import (
    ReqOpCreatePrompt,
    ReqOpDeletePrompt,
    ReqOpDeployPrompt,
    ReqOpGetPrompt,
    ReqOpUpdatePrompt,
    ResOpGetPrompt,
    ResOpGetPromptGroup,
)

op_prompt_api = APIRouter(prefix="/op/prompt", tags=["[관리 페이지] 프롬프트 API"])


@op_prompt_api.post(
    "",
    summary="프롬프트 그룹 코드 생성",
    response_class=Response,
)
async def op_create_prompt(req_body: ReqOpCreatePrompt):
    """
    프롬프트 그룹 코드 생성
    ```
    analysis_code: 분석 코드
    ```
    """
    return await OpPromptService.op_create_prompt(req_body)


@op_prompt_api.put(
    "",
    summary="프롬프트 수정",
    response_class=Response,
)
async def op_update_prompt(req_body: ReqOpUpdatePrompt):
    """
    프롬프트 수정
    ```
    llm_code: LLM 코드
    group: 그룹
    analysis_code: 분석 코드
    prompt: 프롬프트
    ```
    """
    return await OpPromptService.op_update_prompt(req_body)


@op_prompt_api.delete(
    "",
    summary="프롬프트 그룹 코드 삭제",
    response_class=Response,
)
async def op_delete_prompt(req_body: ReqOpDeletePrompt):
    """
    프롬프트 그룹 코드 삭제
    ```
    analysis_code: 분석 코드
    ```
    """

    return await OpPromptService.op_delete_prompt(req_body)


@op_prompt_api.get("", summary="프롬프트 조회", response_model=ResOpGetPrompt)
async def op_get_prompt(
    req_query: Annotated[ReqOpGetPrompt, Depends()],
):
    """
    프롬프트 조회

    ```
    env: op | development | staging | production
    llm_code: LLM 코드
    group: 그룹
    analysis_code: 분석 코드
    ```
    """
    return await OpPromptService.op_get_prompt(req_query)


@op_prompt_api.get(
    "/group",
    summary="프롬프트 그룹 조회",
    response_model=Union[List[ResOpGetPromptGroup], List],
)
async def op_get_prompt_group(env: str = Query(None)):
    """
    프롬프트 그룹 조회
    ```
    env: op | development | staging | production
    ```
    """
    return await OpPromptService.op_get_prompt_group(env)


@op_prompt_api.post(
    "/deploy",
    summary="프롬프트 배포",
    response_class=Response,
)
async def op_deploy_prompt(req_body: ReqOpDeployPrompt):
    """
    프롬프트 배포
    ```
    env: op | development | staging | production
    ```
    """
    return await OpPromptService.op_deploy_prompt(req_body)
