import asyncio
import logging

from fastapi import Response

from api.exceptions import response_error
from api.modules.analysis.analysis_service import AnalysisService
from api.modules.analysis.schema.analysis_schema import ResGetAnalysis
from api.modules_op.dao.op_analysis_dao import (
    create_analysis_code,
    create_last_code,
    delete_analysis,
    deploy_analysis,
    get_analysis,
    get_analysis_codes,
    get_analysis_type_codes,
    is_analysis_code,
    op_get_analysis_task_status_count,
    update_analysis,
)
from api.modules_op.dao.op_analysis_type_dao import (
    deploy_analysis_type,
    get_analysis_types,
    is_analysis_type,
)
from api.modules_op.schema.op_analysis_schema import (
    ReqCreateAnalysisCode,
    ReqDeleteAnalysis,
    ReqDeployAnalysis,
    ReqGetAnalysisPendingProjectCount,
    ReqUpdateAnalysis,
    ResCreateAnalysisCode,
)
from config.const import AI_MODEL, ANALYSIS_ERROR, STATUS
from database.mariadb.mariadb_config import (
    AsyncSessionDev,
    AsyncSessionLocal,
    AsyncSessionOp,
    AsyncSessionPrd,
    AsyncSessionStg,
)

logger = logging.getLogger("app")


class OpAnalysisService:

    @staticmethod
    async def op_create_analysis(req_body: ReqCreateAnalysisCode):
        """
        분석 코드 생성
        """
        try:
            async with AsyncSessionOp() as db:
                # 타입 체크
                if not await is_analysis_type(req_body.type, db):
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_TYPE_NOT_EXIST, ResGetAnalysis
                    )

                # 생성 코드
                code = await create_last_code(req_body.type, db)

                # 코드 생성
                await create_analysis_code(code, req_body.type, db)

                return ResCreateAnalysisCode(code=code)

        except Exception as e:
            logger.error(f"분석 코드 생성 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_get_analysis(env: str, type: str):
        """
        분석 코드 조회
        """
        try:
            env_session_map = {
                "local": AsyncSessionLocal,
                "op": AsyncSessionOp,
                "development": AsyncSessionDev,
                "staging": AsyncSessionStg,
                "production": AsyncSessionPrd,
            }

            if env not in env_session_map:
                return response_error(
                    ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis
                )

            async with env_session_map[env]() as db:
                if not type:
                    # 분석 코드 전체 목록
                    return await get_analysis_codes(db)

                if await is_analysis_type(type, db):
                    # 분석 코드 타입 목록
                    return await get_analysis_type_codes(type, db)

        except Exception as e:
            logger.error(f"분석 코드 목록 조회 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_update_analysis(req_body: ReqUpdateAnalysis):
        """
        분석 수정
        """
        try:
            async with AsyncSessionOp() as db:
                if not await is_analysis_code(req_body.code, db):
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_CODE_NOT_EXIST, ResGetAnalysis
                    )
                await update_analysis(req_body, db)

            return Response(status_code=200)

        except Exception as e:
            logger.error(f"분석 코드 수정 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_delete_analysis(req_body: ReqDeleteAnalysis):
        """
        분석 삭제
        """
        try:
            async with AsyncSessionOp() as db:
                if not await is_analysis_code(req_body.code, db):
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_CODE_NOT_EXIST, ResGetAnalysis
                    )
                await delete_analysis(req_body.code, db)

            return Response(status_code=200)

        except Exception as e:
            logger.error(f"분석 코드 삭제 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_deploy_analysis(req_body: ReqDeployAnalysis):
        """
        분석 배포
        """
        try:
            env = req_body.env

            env_session_map = {
                "local": AsyncSessionLocal,
                "development": AsyncSessionDev,
                "staging": AsyncSessionStg,
                "production": AsyncSessionPrd,
            }

            if env not in env_session_map:
                return response_error(
                    ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis
                )

            async with AsyncSessionOp() as db:
                analysis = await get_analysis(db)
                analysis_type = await get_analysis_types(db)

            async with env_session_map[env]() as db:
                await deploy_analysis_type(analysis_type, db)
                await deploy_analysis(analysis, db)

            return Response(status_code=200)

        except Exception as e:
            logger.error(f"분석 배포 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_get_analysis_task_count():
        """
        분석 pending task 조회 (환경별 병렬 처리)
        """
        try:
            env_session_map = {
                "development": AsyncSessionDev,
                "staging": AsyncSessionStg,
                "production": AsyncSessionPrd,
            }

            async def process_env(env: str, session_factory):
                async with session_factory() as db:
                    # sqs 큐 메세지 수
                    sqs_queue_count = await AnalysisService.get_model_sqs_queue_count(
                        AI_MODEL.WAN
                    )
                    # pending 프로젝트 수
                    pending_project_count = await op_get_analysis_task_status_count(
                        STATUS.PENDING, db
                    )

                    # progress 프로젝트 수
                    progress_project_count = await op_get_analysis_task_status_count(
                        STATUS.PROGRESS, db
                    )
                    logger.info(
                        f"[분석 pending task 조회] env: {env} "
                        f"pending_task_count : {sqs_queue_count.pending} "
                        f"pending_project : {pending_project_count} "
                        f"progress_project : {progress_project_count} "
                        f"progress_task_count : {sqs_queue_count.progress} "
                    )

                    return ReqGetAnalysisPendingProjectCount(
                        env=env,
                        pending_task_count=sqs_queue_count.pending,
                        pending_project_count=pending_project_count,
                        progress_project_count=progress_project_count,
                        progress_task_count=sqs_queue_count.progress,
                    )

            # 환경별 task 생성
            tasks = [
                process_env(env, session_factory)
                for env, session_factory in env_session_map.items()
            ]

            # 병렬 실행
            results = await asyncio.gather(*tasks)
            return results

        except Exception as e:
            logger.error(f"분석 pending task 조회 에러: {e}", exc_info=True)
            raise
