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
    get_process_done_count,
    get_task_engine_all_result,
    is_process_fail,
)
from api.modules.analysis.dao.analysis_task_gradio_dao import (
    update_gradio_result,
    update_task_gradio_code,
    update_task_gradio_end_at,
    update_task_gradio_process,
    update_task_gradio_progress,
    update_task_gradio_prompt,
    update_task_gradio_status,
)
#from api.modules.analysis.json_parser.photo2video_json_parser import result_json
from api.modules.analysis.schema.analysis_schema import DoAnalysisOption, ReqDoAnalysis
# #from api.modules.engine.client.model_api import (
#     api_frame_pack,
#     api_insert_anything_image,
#     api_ltx_distil,
#     api_relight_image,
#     api_sam_mask_image,
#     api_wan,
# )
# from api.modules.engine.engine_service import EngineService
# from api.modules.engine.progress_monitor import run_with_progress
# from api.modules.engine.schema.client_schema import (
#     ModelInputSchema,
#     ReqClientDocumentParser,
#     ReqClientFramePack,
#     ReqClientInsertAnythingImage,
#     ReqClientLtx,
#     ReqClientMaskImage,
#     ReqClientRelight,
#     ReqClientWan,
# )
from api.modules.llm.dao.resource_llm_dao import get_first_priority_llm_code
# from api.modules.llm.llm_chatgpt import (
#     chatgpt_enhance_prompt,
#     chatgpt_photo_music,
#     chatgpt_photo_video,
# )
# from api.modules.llm.llm_gemini import gemini_enhance_prompt, gemini_photo_video
# from api.modules.llm.schema.llm_chatgpt_schema import GPTContext2Video
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
from utils.util import get_mime_type, get_prompt, remove_image_metadata, webp_to_jpg

logger = logging.getLogger("app")


async def ai_gradio_image2image_000001(
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

    video_type = await get_video_type(db, task_id=req_body.taskId)
    
    logger.info(f"video_type : {video_type}")
    return 
    # 기존 task_engine 삭제
    await delete_task_engine(req_body, db)

    for i, option in enumerate(options):
        match option.type:
            case "image":
                logger.info("분석옵션 : AI-PHOTO2VIDEO-000001 image")

            case "prompt":
                logger.info("분석타입 : AI-PHOTO2VIDEO-000001 프롬프트")
                if llm_code == LLM_CODE.LLM_CHATGPT:
                    enhanced_prompt = await chatgpt_enhance_prompt(
                        req_body=req_body,
                        _prompt=_prompt["prompt"],
                        document_file=document_files[i],
                        db=db,
                    )
                if llm_code == LLM_CODE.LLM_GEMINI:
                    enhanced_prompt = await gemini_enhance_prompt(
                        req_body=req_body,
                        _prompt=_prompt["prompt"],
                        document_file=document_files[i],
                        db=db,
                    )

                video_results["results"][i]["video_prompt"] = enhanced_prompt[
                    "video_prompt"
                ]

            case "filter":
                logger.info("분석옵션 : AI-PHOTO2VIDEO-000001 filter")
            case _:
                raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_FAIL)
        # # 엔진 분석 타입 시 SQS 전송
        if video_type == "ENGINE":
            await send_sqs_image_video(
                req_body=req_body,
                documentS3=req_body.documentS3[i],
                video_prompt=video_results["results"][i]["video_prompt"],
                order_no=i + 1,
            )
    video_prompts = [
        video_result["video_prompt"] for video_result in video_results["results"]
    ]

    # llm 결과 저장
    await update_llm_result(req_body, json.dumps(video_results, ensure_ascii=False), db)

    # status progress 변경
    await update_task_gradio_status(req_body, STATUS.PROGRESS, db)

    if video_type == "ENGINE":
        await update_task_gradio_process(req_body, MODEL.WAN2_2.to_json(), db)
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
        await update_task_gradio_process(req_body, MODEL.KLING_V2_1.to_json(), db)

        # API 비디오 요청
        video_bytes = await run_with_progress(
            coro=VideoService.run_multiple_api(
                model=API_VIDEO_MODEL.KLING_V2_1,
                document_files=document_files,
                video_prompts=video_prompts,
            ),
            user_id=req_body.userId,
            project_id=req_body.projectId,
            analysis_code=req_body.type,
            db=db,
            progress=20,
            task_name=f"{API_VIDEO_MODEL.KLING_V2_1} API 비디오 생성중",
        )

        # API 비디오 업로드
        video_urls = await VideoService.upload_video(
            video_bytes=video_bytes,
            document_files=document_files,
            upload_dir=upload_dir,
            s3_path=req_body.analysisS3,
            analysisHttps=req_body.analysisHttps,
        )
    result = await result_json(video_results, video_urls)

    return result


# async def send_sqs_image_video(
#     req_body: ReqDoAnalysis, documentS3: str, video_prompt: str, order_no: int
# ):
#     """
#     photo2video 이미지 to 비디오 SQS 메세지 전송 (WAN2.2)

#     Args:
#         req_body (ReqDoAnalysis): req_body
#         documentS3 (str): 이미지 S3-Key
#         video_prompt (str): video_prompt
#         order_no (int): order_no
#     """

#     logger.info("모델 SQS 메세지 전송")
#     api_endpoint = os.getenv("GUNICORN_API_HOST")
#     wan_queue_url = await get_sqs_queue_url(SQS_QUEUE.WAN)

#     if req_body.test == None:
#         await send_sqs_message(
#             queue_url=wan_queue_url,
#             message=ReqClientWan(
#                 user_id=req_body.userId,
#                 project_id=req_body.projectId,
#                 analysis_code=req_body.type,
#                 env=os.getenv("ENV"),
#                 upload_s3_key=req_body.analysisS3,
#                 document_s3_key=documentS3,
#                 api_endpoint=api_endpoint,
#                 order_no=order_no,
#                 model_input=ModelInputSchema(prompt=video_prompt, shift=3.0),
#             ).model_dump_json(),
#         )
#     else:
#         logger.info(f"모델 테스트 param: {req_body.test}")
#         # 프롬프트 비어 있으면 비디오 프롬프트 적용
#         if req_body.test["prompt"] == "":
#             req_body.test["prompt"] = video_prompt
#             logger.info(video_prompt)
#         await send_sqs_message(
#             queue_url=wan_queue_url,
#             message=ReqClientWan(
#                 user_id=req_body.userId,
#                 project_id=req_body.projectId,
#                 analysis_code=req_body.type,
#                 env=os.getenv("ENV"),
#                 upload_s3_key=req_body.analysisS3,
#                 document_s3_key=documentS3,
#                 api_endpoint=api_endpoint,
#                 order_no=order_no,
#                 model_input=ModelInputSchema(
#                     prompt=req_body.test["prompt"],
#                     negative_prompt=req_body.test["negative_prompt"],
#                     total_second_length=req_body.test["total_second_length"],
#                     frames_per_second=req_body.test["frames_per_second"],
#                     num_inference_steps=req_body.test["num_inference_steps"],
#                     guidance_scale=req_body.test["guidance_scale"],
#                     shift=req_body.test["shift"],
#                     seed=req_body.test["seed"],
#                 ),
#             ).model_dump_json(),
#         )


# async def video_polling(req_body: ReqDoAnalysis, timeout: Optional[int] = 4000):
#     """
#     모델 비디오 생성 폴링 처리 (타임아웃 포함)

#     Args:
#         req_body (ReqDoAnalysis): req_body
#         timeout_sec (int): 최대 대기 시간 (초), 기본 5분
#     """

#     async def _polling():
#         while True:
#             process_fail = await is_process_fail(req_body)
#             if process_fail == True:
#                 raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_FAIL)
#             # task_engine 완료 카운트 조회
#             wan_done_count = await get_process_done_count(req_body)

#             if wan_done_count == len(req_body.documentS3):
#                 logger.info(f"{AI_MODEL.WAN} 모델 실행 완료")
#                 # 비디오 전체 결과 조회
#                 video_s3_urls = await get_task_engine_all_result(req_body)
#                 logger.info(video_s3_urls)

#                 video_urls = [
#                     get_private_s3_key_to_https(
#                         req_body.analysisS3, req_body.analysisHttps, video_s3_url
#                     )
#                     for video_s3_url in video_s3_urls
#                 ]
#                 logger.info(f"video_urls : {video_urls}")
#                 return video_urls

#             await asyncio.sleep(5)

#     try:
#         return await asyncio.wait_for(_polling(), timeout=timeout)
#     except asyncio.TimeoutError:
#         logger.error(f"모델 비디오 생성 timeout: {timeout}초 초과")

#         raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_TIMEOUT)

#     except Exception as e:
#         logger.error(f"모델 비디오 생성 중 에러: {e}", exc_info=True)

#         raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_FAIL)


# async def change_s3_image(req_body: ReqDoAnalysis, delete_s3_path: str, file_path: str):
#     """
#     s3에 업로드된 이미지 파일 교체 (webp -> jpg)

#     Args:
#         delete_s3_path (str): 삭제할 S3 파일 경로
#         upload_s3_path (str): 업로드할 S3 파일 경로
#     """
#     file = os.path.basename(file_path).split(".")[0]
#     s3_path = req_body.analysisS3
#     s3_key = f"{s3_path}videos/{file}.jpg"

#     # S3 파일 삭제
#     await delete_s3(delete_s3_path)

#     # S3 파일 업로드
#     await upload_s3(file_path, s3_key)
