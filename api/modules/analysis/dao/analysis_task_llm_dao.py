import logging

from sqlalchemy import select, update
from sqlalchemy.future import select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_dao import get_analysis_type
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis, TaskLLMSchema
from config.const import STATUS
from database.mariadb.models.resource_llm_model import ResourceLLM
from database.mariadb.models.task_llm_model import TaskLLM

logger = logging.getLogger("app")


async def init_task_llm(req_body: ReqDoAnalysis, db: Session):
    """
    task llm 생성

    Args:
        req_body (ReqDoAnalysis): req_body
        db (Session): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type
    analysis_type = await get_analysis_type(analysis_code, db)

    # 제외할 필드들
    exclude_fields = {
        "id",
        "user_id",
        "project_id",
        "analysis_code",
        "analysis_type",
        "status",
        "progress",
        "request_body",
    }

    # TaskLLM 모델의 컬럼 목록 가져오기
    columns = inspect(TaskLLM).c

    # 제외된 필드를 제외하고 나머지 컬럼에 None 할당
    null_values = {col.name: None for col in columns if col.name not in exclude_fields}

    if await get_task_llm_status(req_body, db) == None:
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
    else:
        task = (
            update(TaskLLM)
            .where(
                TaskLLM.user_id == user_id,
                TaskLLM.project_id == project_id,
                TaskLLM.analysis_code == analysis_code,
            )
            .values(
                user_id=user_id,
                project_id=project_id,
                analysis_code=analysis_code,
                analysis_type=analysis_type,
                status=STATUS.PENDING,
                progress=0,
                request_body=req_body.json(),
                **null_values,
            )
        )

        await db.execute(task)
        await db.commit()


async def get_task_llm(user_id: int, project_id: int, type: str, db: Session):
    """
    task_llm 조회

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


async def get_task_llm_status(req_body: ReqDoAnalysis, db: Session):
    """
    task_llm 조회

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


async def get_task_llm_progress(req_body: ReqDoAnalysis, db: Session):
    """
    task_llm progress 조회

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


async def update_task_llm_progress(req_body: ReqDoAnalysis, progress: int, db: Session):
    """
    task_llm progress 저장

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
        raise Exception("user_id, project_id task_llm row가 없습니다")


async def update_task_llm_status(req_body: ReqDoAnalysis, status: str, db: Session):
    """
    task_llm status 저장

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
        raise Exception("user_id, project_id task_llm row가 없습니다")


async def update_task_llm_result(req_body: ReqDoAnalysis, result: str, db: Session):
    """
    task_llm 분석 결과 저장

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
        raise Exception("user_id, project_id task_llm row가 없습니다")


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
        raise Exception("user_id, project_id task_llm row가 없습니다")


async def update_task_llm_end_at(req_body: ReqDoAnalysis, llm_end_at: str, db: Session):
    """
    task_llm 분석 완료 시간 저장

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
        raise Exception("user_id, project_id task_llm row가 없습니다")


async def update_task_llm_code(req_body: ReqDoAnalysis, db: Session):
    """
    task_llm llm_code 저장

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
        raise Exception("user_id, project_id task_llm row가 없습니다")


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
        raise Exception("user_id, project_id task_llm row가 없습니다")


async def update_task_llm_process(req_body: ReqDoAnalysis, process: str, db: Session):
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
        raise Exception("user_id, project_id task_llm row가 없습니다")


async def get_task_llm_error_message(
    user_id: str, project_id: str, analysis_code: str, db: Session
):
    """
    task_llm 에러 메세지 조회

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


async def update_task_llm_init_error(req_body: ReqDoAnalysis, db: Session):
    """
    task_llm 성공 시 에러 메세지 초기화

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


async def update_task_llm_error(
    req_body: ReqDoAnalysis, error_code: str, error_message: str, db: Session
):
    """
    task_llm 에러 코드 저장

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
    task_llm photo2video 조회

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = req_body.type

    task = select(TaskLLM.photo2video).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )
    result = await db.execute(task)
    return result.scalars().first()


async def update_llm_result(req_body: ReqDoAnalysis, llm_result: str, db: Session):
    """
    task_llm llm_result 저장

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
        .values(llm_result=llm_result)
    )
    await db.execute(task)
    await db.commit()


async def get_ai_photo2video_0000001(req_body: ReqDoAnalysis, db: Session):
    """
    task_llm ai-photo2video-000001 조회

    Args:
        req_body (ReqDoAnalysis): req_body
        db (AsyncSession): DB Session
    """

    user_id = req_body.userId
    project_id = req_body.projectId
    analysis_code = "AI-PHOTO2VIDEO-000001"

    task = select(TaskLLM.llm_result).where(
        TaskLLM.user_id == user_id,
        TaskLLM.project_id == project_id,
        TaskLLM.analysis_code == analysis_code,
    )

    result = await db.execute(task)

    if result == None:
        return None
    return result.scalars().first()


async def update_task_llm_prompt(req_body: ReqDoAnalysis, prompt: str, db: Session):
    """
    task_llm prompt 저장

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
