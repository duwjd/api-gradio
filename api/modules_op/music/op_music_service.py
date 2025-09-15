import json
import logging

from fastapi import Response

from api.exceptions import ResError, response_error
from api.modules_op.dao.op_music_dao import (
    op_create_bgm,
    op_delete_bgm,
    op_get_bgms,
    op_is_music_id,
)
from api.modules_op.schema.op_music_schema import ReqCreateBgm, ReqDeleteBgm
from config.const import ANALYSIS_ERROR, S3
from database.mariadb.mariadb_config import (
    AsyncSessionDev,
    AsyncSessionLocal,
    AsyncSessionOp,
    AsyncSessionPrd,
    AsyncSessionStg,
)
from utils.s3_util_engine import upload_s3_binary

logger = logging.getLogger("app")


class OpMusicService:
    @staticmethod
    async def op_create_bgm(req_body: ReqCreateBgm, binary: bytes):
        """
        op bgm 생성
        """
        try:
            # TODO bgm 생성 시 s3 upload (백엔드에서 binary형태로 받아서 mp3파일 s3에 업로드), db insert 필요
            req_body = req_body.as_dict()

            mood = req_body["mood"]
            filename = req_body["filename"]
            mime_type = req_body["content_type"]

            logger.info(json.dumps(req_body, ensure_ascii=False))

            async with AsyncSessionOp() as db:
                # bgm 생성
                await op_create_bgm(req_body, db)

            # s3 업로드
            bucket = S3.PUBLIC_BUCKET
            s3_key = f"library/sound/bgm/{mood}/{filename}"
            logger.info(s3_key)
            await upload_s3_binary(bucket, s3_key, binary, mime_type)

            return Response(status_code=201)
        except Exception as e:
            logger.error(f"음악 생성 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def op_get_bgms(env: str):
        """
        op 전체 bgm 조회
        """
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
            return await op_get_bgms(db)

    @staticmethod
    async def op_update_bgm():
        """
        op bgm 수정
        """
        # TODO license, name, duration 수정 가능하게 구현, s3에 업로드된 파일 삭제 후 업로드 하게 구현 필요
        async with AsyncSessionOp() as db:
            pass

    @staticmethod
    async def op_delete_bgm(req_body: ReqDeleteBgm):
        """
        op bgm 삭제
        """
        async with AsyncSessionOp() as db:
            if not await op_is_music_id(req_body.music_id, db):
                return response_error(
                    ANALYSIS_ERROR.AI_API_MUSIC_ID_NOT_EXIST, ResError
                )
            await op_delete_bgm(req_body.music_id, db)

        return Response(status_code=200)

    @staticmethod
    async def op_deploy_bgm():
        """
        op bgm 배포
        """
