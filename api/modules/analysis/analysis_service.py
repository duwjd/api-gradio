import asyncio
import json
import logging
import mimetypes
import os
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import BackgroundTasks, Request, Response
from PIL import Image
from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.exceptions import response_error
from api.modules.analysis.dao.analysis_dao import (
    get_analysis_dev,
    get_analysis_group,
    get_analysis_type,
    is_analysis_code,
    update_analysis_sync,
)
from api.modules.analysis.dao.analysis_task_gradio_dao import (
    get_task_gradio,
    get_task_gradio_status,
    init_task_gradio,
    update_task_end_at,
    update_task_gradio_error,
    update_task_gradio_init_error,
    update_task_gradio_progress,
    update_task_gradio_result,
    update_task_gradio_status,
    get_task_gradio_error_message,
)
from api.modules.analysis.processor.assist_processor import ai_assist
from api.modules.analysis.processor_filter import processor_filter
from api.modules.analysis.schema.analysis_schema import (
    ReqDoAnalysis,
    ResDoAnalysis,
    ResGetAnalysis,
)
from config.const import ANALYSIS_ERROR, SQS_QUEUE, STATUS, BaseErrorEnum, MimeType
from database.mariadb.mariadb_config import (
    AsyncSessionDev,
    AsyncSessionLocal,
    SessionLocal,
)
from database.mariadb.models.task_gradio_model import TaskGradio
from utils.s3_util_engine import delete_s3, download_s3, upload_s3
from utils.sqs_util import get_sqs_message_count, get_sqs_queue_url

# utils
from utils.util import build_status_key, is_change_image, webp_to_jpg

logger = logging.getLogger("app")
executor = ThreadPoolExecutor()


class AnalysisService:
    @staticmethod
    async def do_analysis(req_body: ReqDoAnalysis, background_tasks: BackgroundTasks):
        """
        문서 분석 요청을 처리하는 메서드 (비동기 백그라운드 실행)

        Args:
            req (ReqDoAnalysis): 분석 요청 객체 (사용자 ID, 프로젝트 ID, 문서 S3 경로 등 포함)
            request (Request): FastAPI의 요청 객체

        Returns:
            dict: 분석 작업이 시작되었음을 나타내는 응답 메시지

        Example:
            >>> request_data = {"user_id": 1, "project_id": 10, "documentS3": "s3://bucket/file.pdf"}
            >>> response = AnalysisService.잘못된 분석 요청 입니다.(request_data, request)
            {"message": "문서 분석이 백그라운드에서 실행됩니다.", "status": STATUS.SUCCESS}
        """

        try:
            logger.info(f"params: {json.dumps(req_body.dict(), ensure_ascii=False)}")

            # 임시 폴더 생성
            tmp = str(uuid.uuid4())
            base_dir = ".upload"
            upload_dir = os.path.join(base_dir, tmp)
            os.makedirs(upload_dir, exist_ok=True)

            async with AsyncSessionLocal() as db:
                # task code 조회
                is_code = await is_analysis_code(req_body.type, db)
                if is_code:
                    # task 상태 조회
                    status = await get_task_gradio_status(req_body, db)
                    if status == STATUS.PENDING or status == STATUS.PROGRESS:
                        return response_error(
                            ANALYSIS_ERROR.AI_API_ANALYSIS_IS_RUNNING, ResDoAnalysis
                        )

                    # 그룹 체크
                    groups = await get_analysis_group(req_body.type, db)

                    # group이 []면 전체 권한
                    if groups != None:
                        if req_body.group not in groups:
                            raise Exception(ANALYSIS_ERROR.AI_API_GROUP_INVALID)

                    # task_gradio 등록
                    await init_task_gradio(req_body, db)

                    document_files = []
                    if req_body.documentS3 != None:
                        # S3에서 문서 다운로드
                        document_files = [
                            await download_s3(
                                document_file, upload_dir, document_file.split("/")[-1]
                            )
                            for document_file in req_body.documentS3
                        ]

                        # 이미지 전처리 로직, S3 업로드
                        for i, document_file in enumerate(document_files):
                            # 파일 확장자 구하기
                            extention, _ = mimetypes.guess_type(document_file)

                            # 이미지 체크
                            new_file, is_change = await is_change_image(
                                document_file, extention
                            )
                            if is_change == True:
                                extention, _ = mimetypes.guess_type(new_file)
                                file = os.path.basename(new_file)
                                s3_documnt_path = os.path.dirname(
                                    req_body.documentS3[i]
                                )
                                upload_s3_path = f"{s3_documnt_path}/{file}"

                                logger.info(upload_s3_path)

                                # S3 파일 업로드
                                await upload_s3(document_file, upload_s3_path)

                                # documentS3 인덱스 변경
                                req_body.documentS3[i] = upload_s3_path
                                document_files[i] = new_file

                    async def background_task():
                        async with AsyncSessionLocal() as task_db:
                            await AnalysisService._run_analysis(
                                req_body, document_files, upload_dir, task_db
                            )

                    # 백그라운드 동기 병렬 실행
                    background_tasks.add_task(background_task)

                else:
                    raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_REQUEST_INVALID)

            return ResDoAnalysis(
                status=STATUS.SUCCESS,
                message="문서 분석이 백그라운드에서 실행됩니다.",
                documentS3=req_body.documentS3,
            )

        except Exception as e:
            logger.error(f"분석 요청 중 에러: {e}", exc_info=True)

            error_enum = ANALYSIS_ERROR.AI_API_ANALYSIS_FAIL
            error_detail = None

            arg = e.args[0] if e.args else None

            if isinstance(arg, BaseErrorEnum):
                error_enum = arg
                if len(e.args) > 1:
                    error_detail = e.args[1]
            elif isinstance(arg, Exception):
                error_detail = str(arg)

            error_code = error_enum.code
            if error_detail == None:
                error_detail = error_enum.message

            await update_task_gradio_status(req_body, STATUS.FAIL, db)
            await update_task_gradio_error(req_body, error_code, error_detail, db)

            return response_error(error_enum, ResDoAnalysis)

    @staticmethod
    async def get_analysis(user_id: int, project_id: int, type: str, req_app: Request):
        """
        분석 진행 상태를 조회하는 메서드

        Args:
            user_id (int): 사용자 ID
            project_id (int): 프로젝트 ID
            req_app (Request): FastAPI의 요청 객체

        Returns:
            ResGetAnalysis: 분석 진행 상태

        Example:
            >>> response = AnalysisService.get_analysis(1, 10, request)
            {"status": "SUCCESS", "progress": 100}
        """
        try:
            async with AsyncSessionLocal() as db:
                is_code = await is_analysis_code(type, db)
                if is_code == False:
                    # 지원하지 않는 코드 예외처리
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_CODE_NOT_EXIST,
                        ResGetAnalysis,
                    )

                task: TaskLLM = await get_task_gradio(user_id, project_id, type, db)
                if task == None:
                    # 분석 요청 하지 않았을 시 예외처리
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_NOT_REQUEST, ResGetAnalysis
                    )

                status = task.status
                if status == STATUS.PENDING:
                    return ResGetAnalysis(
                        status=STATUS.PENDING,
                        progress=task.progress,
                    )

                if status == STATUS.PROGRESS:
                    return ResGetAnalysis(
                        status=STATUS.PROGRESS,
                        progress=task.progress,
                    )

                if status == STATUS.SUCCESS:
                    return ResGetAnalysis(
                        status=STATUS.SUCCESS,
                        progress=100,
                        type=task.analysis_code,
                        result=json.loads(task.result),
                    )
                if status == STATUS.FAIL:
                    error_code = task.error_code
                    error_enum = getattr(ANALYSIS_ERROR, error_code)

                    return response_error(
                        error_enum,
                        ResGetAnalysis,
                        await get_task_gradio_error_message(
                            user_id=user_id,
                            project_id=project_id,
                            analysis_code=type,
                            db=db,
                        ),
                    )
        except Exception as e:
            logger.error(f"분석 조회 중 에러: {e}", exc_info=True)
            raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_RESPONSE_FAIL)

    @staticmethod
    async def _run_analysis(
        req_body: ReqDoAnalysis, document_files: list, upload_dir: str, db: Session
    ):
        """
        백그라운드에서 AI 분석 실행

        Args:
            req_body(ReqDoAnalysis): 분석 요청 객체
            upload_dir(str): 임시 파일 저장 폴더
            db(Session): DB 연결 객체

        Returns:
            result(list): 분석 결과
        """
        try:
            start_time = time.time()

            result: list = []
            # llm 어시스트
            if req_body.type.startswith("AI-ASSIST"):
                result = await ai_assist(req_body)

            elif req_body.type.startswith("AI-GRADIO-IMAGE2VIDEO"):
                # 분석 진행
                result = await processor_filter(
                    req_body=req_body,
                    document_files=document_files,
                    upload_dir=upload_dir,
                    db=db,
                )
            elif req_body.type.startswith("AI-GRADIO-IMAGE2IMAGE"):
                result = await processor_filter(
                    req_body = req_body,
                    document_files=document_files,
                    upload_dir=upload_dir,
                    db=db,
                )
            if not result:
                logger.error(
                    f"userId: {req_body.userId}, projectId: {req_body.projectId}, analysisCode: {req_body.type} 분석 결과 없음"
                )
                raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_FAIL)

            result = json.dumps(result, ensure_ascii=False)

            await update_task_gradio_result(req_body, result, db)

            end_time = time.time()

            # 상태 업데이트 (완료)
            await update_task_gradio_progress(req_body, 100, db)
            await update_task_gradio_status(req_body, STATUS.SUCCESS, db)
            await update_task_gradio_init_error(req_body, db)
            await update_task_end_at(req_body, round(end_time - start_time, 2), db)

            logger.info(
                f"userId: {req_body.userId}, projectId: {req_body.projectId}, analysisCode: {req_body.type}, 분석 결과 : {result}, 분석 완료 시간 : {round(end_time - start_time, 2)}초"
            )

        except Exception as e:
            logger.error(f"분석 중 에러: {e}", exc_info=True)

            error_enum = ANALYSIS_ERROR.AI_API_ANALYSIS_FAIL
            error_detail = None

            arg = e.args[0] if e.args else None

            if isinstance(arg, BaseErrorEnum):
                error_enum = arg
                if len(e.args) > 1:
                    error_detail = e.args[1]
            elif isinstance(arg, Exception):
                error_detail = str(arg)

            error_code = error_enum.code
            if error_detail == None:
                error_detail = error_enum.message

            await update_task_gradio_status(req_body, STATUS.FAIL, db)
            await update_task_gradio_error(req_body, error_code, error_detail, db)

            return response_error(error_enum, ResDoAnalysis, error_detail)

        finally:
            if os.getenv("ENV") != "local":
                # 사용한 리소스 정리
                shutil.rmtree(upload_dir)

    @staticmethod
    async def sync_resource_analysis():
        """
        resource_analysis 테이블 싱크 업데이트 (dev -> local)
        """
        async with AsyncSessionDev() as db:
            # dev resource_analysis 전체 데이터 가져오기
            analysis = await get_analysis_dev(db)
        with SessionLocal() as db:
            # local resource_analysis 삭제 후 dev 전체 데이터 insert
            update_analysis_sync(analysis, db)

        logger.info("dev -> local resource_analysis 복사 완료")

        return Response(status_code=201, content=None)

    @staticmethod
    async def get_model_sqs_queue_count(model: str):
        """
        SQS큐 메세지 개수 가져오기
        """
        queue_url = await get_sqs_queue_url(model + ".fifo")
        get_sqs_queue_count = await get_sqs_message_count(queue_url)

        return get_sqs_queue_count
