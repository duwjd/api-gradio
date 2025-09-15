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
    분석타입 GRADIO-IMAGE2VIDEO
    """
    logger.info("분석타입 : GRADIO-IMAGE2VIDEO 시작")
    type = req_body.type
    
    if type =="AI-GRADIO-IMAGE2IMAGE-000001":
        result = await ai_gradio_image2image_000001(req_body, upload_dir, document_files, db)
        
    return result