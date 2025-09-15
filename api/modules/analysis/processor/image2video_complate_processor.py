import asyncio
import json
import logging
import mimetypes
import os
import time
from typing import Optional

from sqlalchemy.orm import Session

from api.exceptions import APIException
from api.modules.analysis.dao.analysis_task_engine_dao import get_task_engine_all_result
from api.modules.analysis.json_parser.image2video_json_parser import result_json
from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)
from config.const import ANALYSIS_ERROR, STATUS

logger = logging.getLogger("app")


async def ai_gradio_image2video_000001_complete(req_body: ReqConsumerAnalysis, db: Session):
    """
    image2video 완료 처리
    """
    try:
        video_urls = await get_task_engine_all_result(req_body)
        logger.info(f"video_urls : {video_urls}")

        return video_urls
    except Exception as e:
        logger.error(f"image2video 완료 처리 중 에러: {e}", exc_info=True)
        raise e
