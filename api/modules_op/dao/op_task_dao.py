import logging
from datetime import datetime
from math import ceil

from sqlalchemy import desc, func
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from api.exceptions import ResError, response_error
from api.modules_op.const import OP_ANALYSIS_ERROR
from api.modules_op.schema.op_task_schema import (
    ReqOpGetTaskPagenation,
    ResOpGetTaskList,
    ResOpGetTaskPagenation,
)
from database.mariadb.models.task_llm_model import TaskLLM

logger = logging.getLogger("app")


async def op_get_task_pagingnation(
    req_query: ReqOpGetTaskPagenation,
    db: Session,
):
    """
    op task 페이징네이션 조회 (시작일)
        - 페이지 별 조회
        - 시간 조회 기능 (시작일/시간, 종료일/시간)
    """

    page = req_query.page
    user_id = req_query.user_id
    size = req_query.size
    start_date = req_query.start_date
    end_date = req_query.end_date
    status = req_query.status
    analysis_type = req_query.analysis_type

    filters = []
    try:
        if status != None:
            filters.append(TaskLLM.status == status)

        if start_date != None or end_date != None:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)

            filters.extend(
                [TaskLLM.updated_at >= start_dt, TaskLLM.updated_at <= end_dt]
            )

    except Exception as e:
        logger.error(f"{e}", exc_info=True)
        return response_error(OP_ANALYSIS_ERROR.AI_OP_API_DATE_FORMAT_INVALID, ResError)

    # user_id 조건 추가
    if user_id != None:
        filters.append(TaskLLM.user_id == user_id)

    # analysis_type 조건 추가
    if analysis_type != None:
        filters.append(TaskLLM.analysis_type == analysis_type)

    total_query = select(func.count(TaskLLM.id)).where(*filters)
    total_result = await db.execute(total_query)
    total_count = total_result.scalar_one()
    total_page = ceil(total_count / size) if size > 0 else 0

    query = (
        select(
            TaskLLM.id,
            TaskLLM.user_id,
            TaskLLM.project_id,
            TaskLLM.analysis_code,
            TaskLLM.analysis_type,
            TaskLLM.status,
            TaskLLM.progress,
            TaskLLM.request_body,
            TaskLLM.llm_result,
            TaskLLM.result,
            TaskLLM.end_at,
            TaskLLM.error_code,
            TaskLLM.error_message,
            TaskLLM.created_at,
            TaskLLM.updated_at,
            TaskLLM.deleted_at,
        )
        .where(*filters)
        .order_by(desc(TaskLLM.updated_at))
        .limit(size)
        .offset((page - 1) * size)
    )

    result = await db.execute(query)
    rows = result.mappings().all()

    list = [
        ResOpGetTaskList(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            analysis_code=row["analysis_code"],
            analysis_type=row["analysis_type"],
            status=row["status"],
            progress=row["progress"],
            request_body=row["request_body"],
            llm_result=row["llm_result"],
            result=row["result"],
            end_at=row["end_at"],
            error_code=row["error_code"],
            error_message=row["error_message"],
            created_at=row["created_at"].isoformat() if row["created_at"] else None,
            updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
            deleted_at=row["deleted_at"].isoformat() if row["deleted_at"] else None,
        ).model_dump()
        for row in rows
    ]

    response_data = ResOpGetTaskPagenation(
        total_count=total_count, total_page=total_page, list=list
    )

    return response_data
