import logging

from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_dao import get_analysis_type
from api.modules.analysis.processor.image2video_complate_processor import (
    ai_gradio_image2video_000001_complete,
)
from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)

logger = logging.getLogger("app")


async def processor_complate_filter(
    req_body: ReqConsumerAnalysis,
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
    logger.info("processor complate filter 시작")
    analysis_code = await get_analysis_type(req_body.analysisCode, db)

    match analysis_code:
        case "photo2video":
            return await run_image2video_complete(req_body, db)

        case _:
            logger.error("일치하는 분석코드 없음")


async def run_image2video_complete(req_body: ReqConsumerAnalysis, db: Session):
    """
    분석타입 IMAGE2VIDEO
    """
    analysis_code = req_body.analysisCode

    # photo to video
    if analysis_code == "AI-PHOTO2VIDEO-000001":
        result = await ai_gradio_image2video_000001_complete(req_body, db)

    return result
