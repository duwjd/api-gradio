import asyncio
import json
import logging
from collections import defaultdict

from fastapi import Response

from api.exceptions import response_error
from api.modules.analysis.schema.analysis_schema import ResGetAnalysis
from api.modules_op.const import OP_ANALYSIS_ERROR
from api.modules_op.dao.op_analysis_dao import get_analysis_group
from api.modules_op.llm.op_llm_service import OpLLMService
from api.modules_op.prompt.dao.op_prompt_dao import (
    create_last_prompt_code,
    is_prompt_analyis_code_exist,
    op_create_prompt,
    op_delete_prompt,
    op_deploy_prompt,
    op_get_prompt,
    op_get_prompts,
    op_update_prompt,
)
from api.modules_op.prompt.scema.op_prompt_schema import (
    ReqOpCreatePrompt,
    ReqOpDeletePrompt,
    ReqOpDeployPrompt,
    ReqOpGetPrompt,
    ReqOpUpdatePrompt,
    ResOpGetPrompt,
    ResOpGetPromptGroup,
)
from config.const import AI_MODEL, ANALYSIS_ERROR, STATUS
from config.llm_const import LLM
from database.mariadb.mariadb_config import (
    AsyncSessionDev,
    AsyncSessionLocal,
    AsyncSessionOp,
    AsyncSessionPrd,
    AsyncSessionStg,
)

logger = logging.getLogger("app")


class OpPromptService:
    @staticmethod
    async def op_create_prompt(req_body: ReqOpCreatePrompt):
        """
        OP Prompt 생성
        """
        async with AsyncSessionOp() as db:
            create_count = 0
            # LLM 목록 조회
            llms = await OpLLMService.op_get_llms()
            for i, llm in enumerate(llms):

                # 활성회된 LLM만 처리
                if llm["is_active"] == True:
                    is_prompt_analysis_code = await is_prompt_analyis_code_exist(
                        analysis_code=req_body.analysis_code,
                        llm_code=llm["code"],
                        db=db,
                    )
                    # prompt 분석 코드 없을 시 생성
                    if is_prompt_analysis_code == False:
                        # prompt 코드 생성
                        code = await create_last_prompt_code(db)
                        group = await get_analysis_group(
                            code=req_body.analysis_code, db=db
                        )

                        logger.info(f"group : {group}")

                        if group != None:
                            # prompt 생성
                            await op_create_prompt(
                                group=group,
                                analysis_code=req_body.analysis_code,
                                code=code,
                                llm_code=llm["code"],
                                db=db,
                            )
                            create_count += 1
                            logger.info(
                                f"OP Prompt 생성 code : {code}, analysis_code : {req_body.analysis_code}, llm_code : {llm['code']}"
                            )
        if create_count == 0:
            return response_error(
                OP_ANALYSIS_ERROR.AI_OP_API_PROMPT_CREATE_INVALID,
                ResGetAnalysis,
            )

        return Response(status_code=201)

    @staticmethod
    async def op_get_prompt_group(env: str):
        """
        OP Prompt 그룹 조회
        """
        env_session_map = {
            "local": AsyncSessionLocal,
            "development": AsyncSessionDev,
            "staging": AsyncSessionStg,
            "production": AsyncSessionPrd,
            "op": AsyncSessionOp,
        }

        if env not in env_session_map:
            return response_error(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis)

        async with env_session_map[env]() as db:
            prompts = await op_get_prompts(db)

        # ResOpGetPromptGroup 형태로 파싱
        group_map = defaultdict(set)
        for prompt in prompts:
            if prompt["group"]:

                for g in prompt["group"]:
                    group_map[g].add(prompt["analysis_code"])
            else:
                group_map["common"].add(prompt["analysis_code"])

        result = [
            {"group": g, "analysis_code": list(codes)} for g, codes in group_map.items()
        ]

        result: ResOpGetPromptGroup = sorted(
            result, key=lambda x: (x["group"] != "common", x["group"])
        )

        return result

    @staticmethod
    async def op_get_prompt(req_query: ReqOpGetPrompt):
        """
        OP Prompt 조회
        """
        env = req_query.env
        env_session_map = {
            "local": AsyncSessionLocal,
            "development": AsyncSessionDev,
            "staging": AsyncSessionStg,
            "production": AsyncSessionPrd,
            "op": AsyncSessionOp,
        }

        if env not in env_session_map:
            return response_error(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis)

        async with env_session_map[env]() as db:
            prompt = await op_get_prompt(req_query, db)

        return ResOpGetPrompt(prompt=prompt)

    @staticmethod
    async def op_update_prompt(req_body: ReqOpUpdatePrompt):
        """
        OP Prompt 수정
        """
        async with AsyncSessionOp() as db:
            is_update = await op_update_prompt(req_body, db)
            if is_update == False:
                return response_error(
                    OP_ANALYSIS_ERROR.AI_OP_API_PROMPT_UPDATE_INVALID,
                    ResGetAnalysis,
                )
        return Response(status_code=200)

    @staticmethod
    async def op_delete_prompt(req_body: ReqOpDeletePrompt):
        """
        OP Prompt 삭제
        """
        async with AsyncSessionOp() as db:
            is_delete = await op_delete_prompt(req_body, db)
            if is_delete == False:
                return response_error(
                    OP_ANALYSIS_ERROR.AI_OP_API_PROMPT_DELETE_INVALID,
                    ResGetAnalysis,
                )
        return Response(status_code=200)

    @staticmethod
    async def op_deploy_prompt(req_body: ReqOpDeployPrompt):
        """
        OP Prompt 배포
        """
        env = req_body.env
        env_session_map = {
            "local": AsyncSessionLocal,
            "development": AsyncSessionDev,
            "staging": AsyncSessionStg,
            "production": AsyncSessionPrd,
        }

        if env not in env_session_map:
            return response_error(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis)

        async with AsyncSessionOp() as db:
            # op 프롬프트 조회
            prompt = await op_get_prompts(db)

        async with env_session_map[env]() as db:
            # op 프롬프트 배포
            await op_deploy_prompt(prompt, db)

        return Response(status_code=201)
