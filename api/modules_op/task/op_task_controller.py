from typing import Annotated

from fastapi import APIRouter, Depends

from api.modules_op.schema.op_task_schema import (
    ReqOpGetTaskPagenation,
    ResOpGetTaskPagenation,
)
from api.modules_op.task.op_task_service import OpTaskService

op_task_api = APIRouter(prefix="/op", tags=["[관리 페이지] task API"])


@op_task_api.get(
    "/task",
    summary="task 페이징네이션 조회",
    response_model=ResOpGetTaskPagenation,
)
async def op_get_task_pagingnation(
    req_query: Annotated[ReqOpGetTaskPagenation, Depends()],
):
    """
    task 페이징네이션 조회
    ```
    env : development | staging | production
    user_id: 사용자 ID
    page: 페이지
    size: 사이즈
    startDate: 시작일 (YYYY-MM-DD HH:mm:ss)
    endDate: 종료일 (YYYY-MM-DD HH:mm:ss)
    status: progress | success | fail
    analysis_type: 분석 타입
    ```
    """
    return await OpTaskService.op_get_task_pagingnation(req_query)
