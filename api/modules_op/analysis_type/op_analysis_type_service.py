import logging

from fastapi import Response

from api.exceptions import response_error
from api.modules.analysis.schema.analysis_schema import ResGetAnalysis
from api.modules_op.dao.op_analysis_type_dao import (
    create_analysis_type,
    delete_analysis_type,
    get_analysis_types,
    is_analysis_type,
    update_analysis_type,
)
from api.modules_op.schema.op_analyis_type_schema import (
    ReqCreateAnalysisType,
    ReqDeleteAnalysisType,
    ReqUpdateAnalysisType,
)
from config.const import ANALYSIS_ERROR
from database.mariadb.mariadb_config import (
    AsyncSessionDev,
    AsyncSessionLocal,
    AsyncSessionOp,
    AsyncSessionPrd,
    AsyncSessionStg,
)

logger = logging.getLogger("app")


class OpAnalysisTypeService:

    @staticmethod
    async def op_create_analysis_type(req_body: ReqCreateAnalysisType):
        """
        분석 타입 생성
        """
        try:
            async with AsyncSessionOp() as db:
                if await is_analysis_type(req_body.type, db):
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_TYPE_EXIST, ResGetAnalysis
                    )
                # 분석 타입 생성
                await create_analysis_type(req_body, db)

            return Response(status_code=201)

        except Exception as e:
            logger.error(f"분석 타입 생성 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_get_analysis_types():
        """
        분석 타입 목록
        """
        try:
            async with AsyncSessionOp() as db:
                return await get_analysis_types(db)

        except Exception as e:
            logger.error(f"분석 타입 목록 조회 중 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_update_analysis_type(req_body: ReqUpdateAnalysisType):
        """
        분석 타입 수정
        """
        try:
            async with AsyncSessionOp() as db:
                if not await is_analysis_type(req_body.type, db):
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_TYPE_NOT_EXIST, ResGetAnalysis
                    )
                # 분석 타입 수정
                await update_analysis_type(req_body, db)

            return Response(status_code=200)

        except Exception as e:
            logger.error(f"분석 타입 수정 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_delete_analysis_type(req_body: ReqDeleteAnalysisType):
        """
        분석 타입 삭제
        """
        try:
            async with AsyncSessionOp() as db:
                if not await is_analysis_type(req_body.type, db):
                    return response_error(
                        ANALYSIS_ERROR.AI_API_ANALYSIS_TYPE_NOT_EXIST, ResGetAnalysis
                    )
                # 분석 타입 삭제
                await delete_analysis_type(req_body, db)

            return Response(status_code=200)

        except Exception as e:
            logger.error(f"분석 타입 삭제 에러: {e}", exc_info=True)
            raise e
