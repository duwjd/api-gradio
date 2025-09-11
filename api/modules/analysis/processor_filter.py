import logging
import os
import uuid

from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_dao import get_analysis_type

from api.modules.analysis.processor.image2video_processor import (
    ai_gradio_image2video_000001,
)

from api.modules.analysis.processor.image2image_processor import (
    ai_gradio_image2image_000001,
)
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis, ResDoAnalysis
from config.const import ANALYSIS_ERROR
from utils.util import get_mime_type, get_prompt

logger = logging.getLogger("app")


async def processor_filter(
    req_body: ReqDoAnalysis,
    document_files: list,
    upload_dir: str,
    db: Session,
):
    """
    processor 분기 처리

    Args:
        req_body(ReqDoAnalysis): 분석 요청 객체
        upload_dir(str): 임시 파일 저장 폴더
        db(Session): DB 연결 객체

    Returns:
        result(list): 분석 결과
    """
    logger.info("processor filter 시작")
    type = await get_analysis_type(req_body.type, db)

    logger.info(type)
    match type:
        case "gradio-image2video":
            return await run_gradio_image2video(req_body, document_files, upload_dir, db)
        case "gradio-image2image":
            return await run_gradio_image2image(req_body, document_files, upload_dir, db)
        case _:
            logger.error("일치하는 분석코드 없음")


async def run_gradio_image2video(req_body: ReqDoAnalysis, document_files:list, upload_dir: str, db: Session):
    """
    분석타입 GRADIO-IMAGE2VIDEO
    """
    logger.info("분석타입 : GRADIO-IMAGE2VIDEO 시작")
    type = req_body.type
    
    if type =="AI-GRADIO-IMAGE2VIDEO-000001":
        result = await ai_gradio_image2video_000001(req_body, upload_dir, document_files, db)
    
    return result
    
    

async def run_gradio_image2image(req_body: ReqDoAnalysis, document_files:list, upload_dir: str, db: Session):
    """
    분석타입 GRADIO-I2V
    """
    logger.info("분석타입 : GRADIO-I2V 시작")
    type = req_body.type
    
    if type =="AI-GRADIO-IMAGE2IMAGE-000001":
        result = await ai_gradio_image2image_000001(req_body, upload_dir, document_files, db)
        
    return result
    
# async def run_analysis(req_body: ReqDoAnalysis, upload_dir: str, db: Session):
    
#     """
#     분석타입 ANALYSIS
#     """
#     logger.info("분석타입 : ANALYSIS 시작")
#     type = req_body.type

#     # S3에서 문서 다운로드
#     document_file_path = await download_s3(
#         req_body.documentS3[0], upload_dir, str(uuid.uuid4())
#     )

#     if not os.path.exists(document_file_path):
#         raise Exception(ANALYSIS_ERROR.AI_API_FILE_DOWNLOAD_FAIL, ResDoAnalysis)

#     logger.info(f"파일 다운로드 완료: {document_file_path}")

#     # banner to video(자동차)
#     if type == "AI-ANALYSIS-000003":
#         if isinstance(req_body.prompt[0]["prompt"], dict):
#             _prompt = req_body.prompt[0]["prompt"]
#         else:
#             _prompt = get_prompt(
#                 llm_code=req_body.prompt[0]["llmCode"],
#                 group=req_body.group,
#                 doc_type=req_body.type,
#             )

#         # MIME Type 확인
#         mime_type = get_mime_type(document_file_path)
#         result = await ai_analysis_000003(
#             _prompt,
#             document_file_path,
#             mime_type,
#             req_body,
#             db,
#         )

#     if type == "AI-ANALYSIS-000004":
#         if isinstance(req_body.prompt[0]["prompt"], dict):
#             _prompt = req_body.prompt[0]["prompt"]
#         else:
#             _prompt = get_prompt(
#                 llm_code=req_body.prompt[0]["llmCode"],
#                 group=req_body.group,
#                 doc_type=req_body.type,
#             )

#         # MIME Type 확인
#         mime_type = get_mime_type(document_file_path)
#         result = await ai_analysis_000004(
#             _prompt,
#             document_file_path,
#             mime_type,
#             req_body,
#             db,
#         )

#     return result


# async def run_analysis_test(req_body: ReqDoAnalysis, upload_dir: str):
#     """
#     분석타입 ANALYSIS_TEST
#     """
#     logger.info("분석타입 : ANALYSIS-TEST 시작")
#     type = req_body.type

#     # S3에서 문서 다운로드
#     document_file_path = await download_s3(
#         req_body.documentS3[0], upload_dir, str(uuid.uuid4())
#     )

#     # banner to video(자동차)
#     if type == "AI-ANALYSIS-TEST-000003":
#         # MIME Type 확인
#         mime_type = get_mime_type(document_file_path)
#         result = await ai_analysis_test_000003(mime_type)

#     return result


# async def run_photo2video(
#     req_body: ReqDoAnalysis, document_files: list, upload_dir: str, db: Session
# ):
#     """
#     분석타입 PHOTO2VIDEO
#     """
#     logger.info("분석타입 : PHOTO2VIDEO 시작")
#     type = req_body.type

#     # # S3에서 문서 다운로드
#     document_files = [
#         await download_s3(document_file, upload_dir, document_file.split("/")[-1])
#         for document_file in req_body.documentS3
#     ]

#     # photo to video
#     if type == "AI-PHOTO2VIDEO-000001":
#         result = await ai_photo2video_000001(req_body, upload_dir, document_files, db)
#     elif type == "AI-PHOTO2VIDEO-000002":
#         result = await ai_photo2video_000002(req_body, upload_dir, document_files, db)
#     elif type == "AI-PHOTO2VIDEO-000003":
#         result = await ai_photo2video_000003(req_body, upload_dir, document_files, db)
#     elif type == "AI-PHOTO2VIDEO-000004":
#         result = await ai_photo2video_000004(req_body, upload_dir, document_files, db)
#     elif type == "AI-PHOTO2VIDEO-000005":
#         result = await ai_photo2video_000005(req_body, upload_dir, document_files, db)
#     elif type == "AI-PHOTO2VIDEO-000006":
#         result = await ai_photo2video_000006(req_body, upload_dir, document_files, db)

#     return result