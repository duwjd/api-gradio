import logging
from typing import List

from fastapi import Response

from api.exceptions import response_error
from api.modules.analysis.schema.analysis_schema import ResGetAnalysis
from api.modules_op.dao.op_llm_dao import op_get_llms, op_update_llm
from api.modules_op.schema.op_llm_schema import ReqUpdateLLM, ResGetLLM
from database.mariadb.mariadb_config import AsyncSessionOp

logger = logging.getLogger("app")
from config.const import ANALYSIS_ERROR


class OpLLMService:
    @staticmethod
    async def op_get_llms():
        """
        LLM 목록 조회
        """
        try:
            async with AsyncSessionOp() as db:
                llms = await op_get_llms(db)
                return llms

        except Exception as e:
            logger.error(f"LLM 목록 조회 중 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_update_llm(req_body: List[ReqUpdateLLM]):
        """
        LLM 수정
        """
        try:
            # 우선순위 중복 체크
            priorities = [item.priority for item in req_body]
            is_priority_duplicate = len(priorities) != len(set(priorities))
            if is_priority_duplicate:
                return response_error(
                    ANALYSIS_ERROR.AI_API_LLM_PRIORITY_DUPLICATE, ResGetAnalysis
                )

            async with AsyncSessionOp() as db:
                await op_update_llm(req_body, db)
                return Response(status_code=200)

        except Exception as e:
            logger.error(f"LLM 수정중 에러: {e}", exc_info=True)
            raise e
