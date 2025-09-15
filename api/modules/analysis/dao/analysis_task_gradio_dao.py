import logging
import json
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, update
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_dao import get_analysis_type
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis, TaskLLMSchema
from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)
from config.const import STATUS
from database.mariadb.models.resource_llm_model import ResourceLLM
from database.mariadb.models.task_llm_model import TaskLLM

logger = logging.getLogger("app")


async def init_task_gradio(req_body: ReqDoAnalysis, db: Session):
    """
    task gradio 생성 : 요청이 들어오면 새로운 row 생성

    Args:
        req_body (ReqDoAnalysis): req_body
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type
    analysis_type = await get_analysis_type(analysis_code, db)

    # 항상 새로운 태스크 생성
    task = TaskLLM(
        user_id=user_id,
        project_id=project_id,
        analysis_code=analysis_code,
        analysis_type=analysis_type,
        status=STATUS.PENDING,
        progress=0,
        request_body=req_body.json(),
    )

    db.add(task)
    await db.commit()


async def get_task_gradio(user_id: int, project_id: int, type: str, db: Session):
    """
    task_gradio 조회

    Args:
        user_id (int): 사용자 ID
        project_id (int): 프로젝트 ID
        type (str): 분석 코드
        db (Session): DB Session

    Returns:
        TaskLLM: db 조회 결과

    """
    analysis_code = type

    # 코드 데이터 조회
    query = select(TaskLLM).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )
    result = await db.execute(query)
    task = result.scalars().first()

    if task:
        return TaskLLMSchema.model_validate(task)
    return None


async def get_task_gradio_status(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio 조회

    Args:
        req_body(ReqDoAnalysis): req_body
        db (Session): DB Session

    Returns:
        TaskLLM: db 조회 결과

    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    query = select(TaskLLM).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )
    result = await db.execute(query)
    task = result.scalars().first()

    if task:
        return TaskLLMSchema.model_validate(task).status
    return None


async def get_task_gradio_progress(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio progress 조회

    Args:
        req_body(ReqDoAnalysis): req_body
        db (Session): DB Session

    Returns:
        progress(int): 진행률

    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    query = select(TaskLLM).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )
    result = await db.execute(query)
    task = result.scalars().first()

    if task:
        return TaskLLMSchema.model_validate(task).progress
    return 0


async def update_task_gradio_progress(req_body: ReqDoAnalysis, progress: int, db: Session):
    """
    task_gradio progress 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        progress (int): 진행율
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(progress=progress)
    )

    result = await db.execute(task)
    await db.commit()

    # logger.info(
    #     f"[분석 진행률] user_id: {req_body.userId}, project_id: {req_body.projectId}, analysis_code: {req_body.type}, progress: {progress}"
    # )

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_task_gradio_status(req_body: ReqDoAnalysis, status: str, db: Session):
    """
    task_gradio status 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        status (str): 상태
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(status=status)
    )

    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_task_gradio_result(req_body: ReqDoAnalysis, result: str, db: Session):
    """
    task_gradio 분석 결과 저장

    Args:
        req_body (ReqDoAnalysis)
        result (str): 분석 결과
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(result=result)
    )

    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_task_end_at(req_body: ReqDoAnalysis, end_at: str, db: Session):
    """
    task 분석 완료 시간 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        end_at (str): 분석 완료 시간
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(end_at=end_at)
    )

    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_task_gradio_end_at(req_body: ReqDoAnalysis, llm_end_at: str, db: Session):
    """
    task_gradio 분석 완료 시간 저장

    Args:
        req_body (ReqDoAnalysis)
        llm_end_at (str): llm 분석 완료 시간
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(llm_end_at=llm_end_at)
    )

    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_task_gradio_code(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio llm_code 저장

    Args:
        req_body (ReqDoAnalysis)
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    llm_code_query = select(ResourceLLM.code).where(ResourceLLM.priority == 1)
    result = await db.execute(llm_code_query)
    llm_code = result.scalars().first()

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(llm_code=llm_code)
    )

    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_empty_tag_llm(req_body: ReqDoAnalysis, empty_tag: str, db: Session):
    """
    empty_tag 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        empty_tag (str): 분석 결과 빈 태그
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(empty_tag=empty_tag)
    )
    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def update_task_gradio_process(req_body: ReqDoAnalysis, process: str, db: Session):
    """
    분석 프로세스 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        process (str): 분석 프로세스
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(process=process)
    )
    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")


async def get_task_gradio_error_message(
    user_id: str, project_id: str, analysis_code: str, db: Session
):
    """
    task_gradio 에러 메세지 조회

    Args:
        req_body (ReqDoAnalysis): req_body
        db (Session): DB Session

    Returns:
        error_message (str): 에러 메세지
    """

    task = select(TaskLLM.error_message).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )

    result = await db.execute(task)
    error_message = result.scalars().first()

    if error_message:
        return error_message
    return None


async def update_task_gradio_init_error(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio 성공 시 에러 메세지 초기화

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(error_code=None, error_message=None)
    )
    await db.execute(task)
    await db.commit()


async def update_task_gradio_error(
    req_body: ReqDoAnalysis, error_code: str, error_message: str, db: Session
):
    """
    task_gradio 에러 코드 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        error_code (str): 에러 코드
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(
            error_code=error_code,
            error_message=error_message,
        )
    )
    await db.execute(task)
    await db.commit()


async def get_photo2video(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio image2video 조회

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = select(TaskLLM.image2video).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )
    result = await db.execute(task)
    return result.scalars().first()

async def get_task_gradio_request_body(req_body: ReqConsumerAnalysis, db: AsyncSession):
    """
    task_gradio documentS3 조회

    Args:
        req_body (ReqConsumerAnalysis): req_body
        db (Session): DB Session

    Returns:
        documentS3 (list): input url 주소 리스트
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.analysisCode

    task = select(TaskLLM.request_body).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )

    result = await db.execute(task)
    request_body = result.scalars().first()

    if request_body:
        data = json.loads(request_body)
        return ReqDoAnalysis(**data)
    return None

async def update_task_gradio_request_body(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio request_body 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        request_body (str): request_body
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(request_body=req_body.model_dump_json())
    )

    result = await db.execute(task)
    await db.commit()

    if result.rowcount == 0:
        raise Exception("user_id, project_id task_gradio row가 없습니다")



async def update_gradio_result(req_body: ReqDoAnalysis, gradio_result: str, db: Session):
    """
    task_gradio llm_result 저장

    Args:
        req_body (ReqDoAnalysis): req_body
        llm_result (str): llm 전체 결과
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(llm_result=gradio_result)
    )
    await db.execute(task)
    await db.commit()


async def get_ai_gradio_image2video_0000001(req_body: ReqDoAnalysis, db: Session):
    """
    task_gradio ai-gradio_image2video-000001 조회

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = "AI-GRADIO-IMAGE2VIDEO-000001"

    task = select(TaskLLM.llm_result).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )

    result = await db.execute(task)

    if result == None:
        return None
    return result.scalars().first()


async def update_task_gradio_prompt(req_body: ReqDoAnalysis, prompt: str, db: Session):
    """
    task_gradio prompt 저장

    Args:
        prompt (str): prompt
        db (Session): DB Session
    """
    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    prompt = (
        update(TaskLLM)
        .where(
            TaskLLM.user_id == user_id,
            TaskLLM.project_id == project_id,
            TaskLLM.analysis_code == analysis_code,
        )
        .values(prompt=prompt)
    )

    await db.execute(prompt)
    await db.commit()
