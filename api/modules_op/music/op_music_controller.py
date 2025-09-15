from typing import List, Optional, Union

from fastapi import APIRouter, File, Form, Query, UploadFile

from api.modules_op.music.op_music_service import OpMusicService
from api.modules_op.schema.op_music_schema import (
    ReqCreateBgm,
    ReqDeleteBgm,
    ReqUpdateBgm,
    ResGetBgm,
)

op_music_api = APIRouter(prefix="/op", tags=["[관리 페이지] 배경음악 API"])


@op_music_api.post("/bgm", summary="음악 생성", status_code=201)
async def op_create_bgm(
    license: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    duration: Optional[int] = Form(None),
    mood: Optional[str] = Form(None),
    file: UploadFile = File(...),
):
    """
    배경음악 생성

    multipart/form-data 형태로 request body 제공
    """

    req_body = ReqCreateBgm(
        license=license,
        name=name,
        duration=duration,
        mood=mood,
        file=file,
    )

    # file binary 읽기
    binary = await file.read()

    return await OpMusicService.op_create_bgm(req_body, binary)


@op_music_api.get(
    "/bgm", summary="음악 조회", response_model=Union[List[ResGetBgm], List]
)
async def op_get_bgms(
    env: str = Query(None),
):
    """
    배경음악 조회
    """
    return await OpMusicService.op_get_bgms(env)


@op_music_api.put("/bgm", summary="음악 수정")
async def op_update_bgm(req_body: ReqUpdateBgm):
    """
    배경음악 수정
    """


@op_music_api.delete("/bgm", summary="음악 삭제")
async def op_delete_bgm(req_body: ReqDeleteBgm):
    """
    배경음악 삭제
    """
    return await OpMusicService.op_delete_bgm(req_body)


@op_music_api.post("/bgm/deploy", summary="음악 배포")
async def op_deploy_bgm(req_body: ReqDeleteBgm):
    """
    배경음악 삭제
    """
