import logging
from typing import Optional

from api.exceptions import ResError, response_error
from api.modules_op.dao.op_task_dao import op_get_task_pagingnation
from api.modules_op.schema.op_task_schema import ReqOpGetTaskPagenation
from config.const import ANALYSIS_ERROR
from database.mariadb.mariadb_config import (
    AsyncSessionDev,
    AsyncSessionLocal,
    AsyncSessionOp,
    AsyncSessionPrd,
    AsyncSessionStg,
)

logger = logging.getLogger("app")


class OpTaskService:

    @staticmethod
    async def op_get_task_pagingnation(
        req_query: ReqOpGetTaskPagenation,
    ):
        """
        task 페이징네이션 목록 조회

        Args:
            env (str): development | staging | production
            page (int): 페이지
            size (int): 사이즈
            startDate (str): 시작일 (YYYY-MM-DD HH:mm:ss)
            endDate (str): 종료일 (YYYY-MM-DD HH:mm:ss)
            status (str): progress | success | fail

        Returns:
            ResOpGetTaskPagenation: task 페이징네이션 목록
        """
        try:
            env = req_query.env
            env_session_map = {
                "local": AsyncSessionLocal,
                "op": AsyncSessionOp,
                "development": AsyncSessionDev,
                "staging": AsyncSessionStg,
                "production": AsyncSessionPrd,
            }

            if env not in env_session_map:
                return response_error(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResError)

            async with env_session_map[env]() as db:
                # task 페이징네이션 목록 조회
                return await op_get_task_pagingnation(req_query, db)
        except Exception as e:
            logger.error(f"op task 페이징네이션 조회 에러: {e}", exc_info=True)
            raise e
