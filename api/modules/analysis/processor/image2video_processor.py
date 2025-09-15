import asyncio
import json
import logging
import mimetypes
import os
import time
from typing import Optional

import openai
from PIL import features
from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_resource_video_model_dao import (
    get_video_type,
)
from api.modules.analysis.dao.analysis_task_engine_dao import (
    delete_task_engine,
    init_task_engine,
    get_process_done_count,
    get_task_engine_all_result,
    is_process_fail,
)
from api.modules.analysis.dao.analysis_task_llm_dao import (
    update_task_llm_result,
    update_task_llm_code,
    update_task_llm_end_at,
    update_task_llm_process,
    update_task_llm_progress,
    update_task_llm_prompt,
    update_task_llm_status,
)

from api.modules.analysis.json_parser.image2video_json_parser import result_json
from api.modules.analysis.schema.analysis_schema import DoAnalysisOption, ReqDoAnalysis

from api.modules.engine.progress_monitor import run_with_progress
from api.modules.engine.schema.client_schema import (
    ModelInputSchema,
    ReqClientWan,
)

from api.modules.video.video_service import VideoService
from config.const import (
    AI_MODEL,
    ANALYSIS_ERROR,
    API_MUSIC_MODEL,
    API_VIDEO_MODEL,
    LLM_CODE,
    MODEL,
    SQS_QUEUE,
    STATUS,
    MimeType,
)

# utils
from utils.s3_util_engine import delete_s3, get_private_s3_key_to_https, upload_s3
from utils.sqs_util import get_sqs_queue_url, send_sqs_message
from utils.util import get_prompt_from_request_body

logger = logging.getLogger("app")


async def ai_gradio_image2video_000001(
    req_body: ReqDoAnalysis,
    upload_dir: str,
    document_files: list,
    db: Session,
):
    """
    gradio_image2video_000001
    """
    logger.info("분석코드 : AI-GRADIO-IMAGE2VIDEO-000001 시작")
    options = req_body.option
    if options == None:
        raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_OPTION_NOT_EXIST)

    logger.info(
        f"user_id: {req_body.userId}, project_id: {req_body.projectId}, analysis_code: {req_body.type}, options: {options}"
    )

    # 기존 task_engine 삭제
    await delete_task_engine(req_body, db)


    for idx, opt in enumerate(options):
        logger.info(f"options[{idx}]: {opt}")  # idx는 정수, opt는 DoAnalysisOption 객체

        # ENGINE or API
        video_type = await get_video_type(db)
        logger.info(f"video_type : {video_type}")
        
        # 어떤 모델 쓸 건지 가져오기
        video_model = opt.model["name"]   # opt는 DoAnalysisOption 객체
        logger.info(f"video_model : {video_model}")
        
        # 사용자가 입력한 프롬프트 가져오기
        userinput_prompt = get_prompt_from_request_body(req_body)
        logger.info(f"사용자가 입력한 프롬프트 : {userinput_prompt}")
        
        if video_type == "API":
            await update_task_llm_process(req_body, MODEL.KLING_V2_1.to_json(), db)

            video_bytes = await run_with_progress(
                coro=VideoService.run_multiple_api(
                    model=video_model,
                    document_files=document_files,
                    video_prompts=userinput_prompt,
                ),
                user_id=req_body.userId,
                project_id=req_body.projectId,
                analysis_code=req_body.type,
                db=db,
                progress=20,
                task_name=f"{video_model} API 비디오 생성중",
            )

            video_urls = await VideoService.upload_video(
                video_bytes=video_bytes,
                document_files=document_files,
                upload_dir=upload_dir,
                s3_path=req_body.analysisS3,
                analysisHttps=req_body.analysisHttps,
            )

        if video_type == "ENGINE":
            # task_engine에 추가해됨
            for i, document_file in enumerate(document_files):
                # task_engine 초기화
                await init_task_engine(req_body, i + 1, MODEL.WAN2_2.to_json(), db)
            
            await send_sqs_image_video(
                req_body=req_body,
                documentS3=req_body.documentS3[idx],  # idx는 정수
                video_prompt=userinput_prompt,
                order_no=idx + 1,   # i 대신 idx 사용
            )
        
    # status progress 변경
    await update_task_llm_status(req_body, STATUS.PROGRESS, db)

    if video_type == "ENGINE":
        await update_task_llm_process(req_body, MODEL.WAN2_2.to_json(), db)
        # 모델 비디오 생성 폴링 처리
        video_urls = await run_with_progress(
            coro=video_polling(req_body),
            user_id=req_body.userId,
            project_id=req_body.projectId,
            analysis_code=req_body.type,
            db=db,
            progress=20,
            task_name=f"{AI_MODEL.WAN} 모델 비디오 생성중",
        )
    if video_type == "API":
        # process
        await update_task_llm_process(req_body, MODEL.KLING_V2_1.to_json(), db)

        # API 비디오 요청
        video_bytes = await run_with_progress(
            coro=VideoService.run_multiple_api(
                model=video_model,
                document_files=document_files,
                video_prompts=userinput_prompt,
            ),
            user_id=req_body.userId,
            project_id=req_body.projectId,
            analysis_code=req_body.type,
            db=db,
            progress=20,
            task_name=f"{video_model} API 비디오 생성중",
        )

        # API 비디오 업로드
        video_urls = await VideoService.upload_video(
            video_bytes=video_bytes,
            document_files=document_files,
            upload_dir=upload_dir,
            s3_path=req_body.analysisS3,
            analysisHttps=req_body.analysisHttps,
        )
    result = await result_json(video_urls)

    return result


async def send_sqs_image_video(
    req_body: ReqDoAnalysis, documentS3: str, video_prompt: str, order_no: int
):
    """
    photo2video 이미지 to 비디오 SQS 메세지 전송 (WAN2.2)

    Args:
        req_body (ReqDoAnalysis): req_body
        documentS3 (str): 이미지 S3-Key
        video_prompt (str): video_prompt
        order_no (int): order_no
    """
    logger.info("모델 SQS 메세지 전송")
    api_endpoint = os.getenv("GUNICORN_API_HOST")

    env = os.getenv("ENV")

    match env:
        case "gradio":
            wan_queue_url = await get_sqs_queue_url(SQS_QUEUE.GRADIO_WAN_REQUEST)
        case "local":
            wan_queue_url = await get_sqs_queue_url(SQS_QUEUE.LOCAL_WAN_REQUEST)
        case "development":
            wan_queue_url = await get_sqs_queue_url(SQS_QUEUE.DEV_WAN_REQUEST)
        case "staging":
            wan_queue_url = await get_sqs_queue_url(SQS_QUEUE.STG_WAN_REQUEST)
        case "production":
            wan_queue_url = await get_sqs_queue_url(SQS_QUEUE.PRD_WAN_REQUEST)

    if req_body.test == None:
        await send_sqs_message(
            queue_url=wan_queue_url,
            message=ReqClientWan(
                userId=req_body.userId,
                projectId=req_body.projectId,
                analysisCode=req_body.type,
                env=os.getenv("ENV"),
                uploadS3Key=req_body.analysisS3,
                documentS3Key=documentS3,
                orderNo=order_no,
                modelInput=ModelInputSchema(prompt=video_prompt, shift=3.0),
            ).model_dump_json(by_alias=True),
        )
        logger.info(f"""Okay lets see message: \n{ReqClientWan(
                userId=req_body.userId,
                projectId=req_body.projectId,
                analysisCode=req_body.type,
                env=os.getenv("ENV"),
                uploadS3Key=req_body.analysisS3,
                documentS3Key=documentS3,
                orderNo=order_no,
                modelInput=ModelInputSchema(prompt=video_prompt, shift=3.0),
            ).model_dump_json(by_alias=True)}""")
    else:
        logger.info(f"모델 테스트 param: {req_body.test}")
        # 프롬프트 비어 있으면 비디오 프롬프트 적용
        if req_body.test["prompt"] == "":
            req_body.test["prompt"] = video_prompt
            logger.info(video_prompt)
        await send_sqs_message(
            queue_url=wan_queue_url,
            message=ReqClientWan(
                userId=req_body.userId,
                projectId=req_body.projectId,
                analysisCode=req_body.type,
                env=os.getenv("ENV"),
                uploadS3Key=req_body.analysisS3,
                documentS3Key=documentS3,
                apiEndpoint=api_endpoint,
                orderNo=order_no,
                modelInput=ModelInputSchema(
                    prompt=req_body.test["prompt"],
                    negativePrompt=req_body.test["negative_prompt"],
                    totalSecondLength=req_body.test["total_second_length"],
                    framesPerSecond=req_body.test["frames_per_second"],
                    numInferenceSteps=req_body.test["num_inference_steps"],
                    guidanceScale=req_body.test["guidance_scale"],
                    shift=req_body.test["shift"],
                    seed=req_body.test["seed"],
                ),
            ).model_dump_json(by_alias=True),
        )

async def video_polling(req_body: ReqDoAnalysis, timeout: Optional[int] = 4000):
    """
    모델 비디오 생성 폴링 처리 (타임아웃 포함)

    Args:
        req_body (ReqDoAnalysis): req_body
        timeout_sec (int): 최대 대기 시간 (초), 기본 5분
    """

    async def _polling():
        while True:
            process_fail = await is_process_fail(req_body)
            if process_fail == True:
                raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_FAIL)
            # task_engine 완료 카운트 조회
            wan_done_count = await get_process_done_count(req_body)

            if wan_done_count == len(req_body.documentS3):
                logger.info(f"{AI_MODEL.WAN} 모델 실행 완료")
                # 비디오 전체 결과 조회
                video_s3_urls = await get_task_engine_all_result(req_body)
                logger.info(video_s3_urls)

                video_urls = [
                    get_private_s3_key_to_https(
                        req_body.analysisS3, req_body.analysisHttps, video_s3_url
                    )
                    for video_s3_url in video_s3_urls
                ]
                logger.info(f"video_urls : {video_urls}")
                return video_urls

            await asyncio.sleep(5)

    try:
        return await asyncio.wait_for(_polling(), timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"모델 비디오 생성 timeout: {timeout}초 초과")

        raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_TIMEOUT)

    except Exception as e:
        logger.error(f"모델 비디오 생성 중 에러: {e}", exc_info=True)

        raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_FAIL)


async def change_s3_image(req_body: ReqDoAnalysis, delete_s3_path: str, file_path: str):
    """
    s3에 업로드된 이미지 파일 교체 (webp -> jpg)

    Args:
        delete_s3_path (str): 삭제할 S3 파일 경로
        upload_s3_path (str): 업로드할 S3 파일 경로
    """
    file = os.path.basename(file_path).split(".")[0]
    s3_path = req_body.analysisS3
    s3_key = f"{s3_path}videos/{file}.jpg"

    # S3 파일 삭제
    await delete_s3(delete_s3_path)

    # S3 파일 업로드
    await upload_s3(file_path, s3_key)
