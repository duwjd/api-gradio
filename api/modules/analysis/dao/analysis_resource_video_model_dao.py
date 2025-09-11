from sqlalchemy import select
from sqlalchemy.orm import Session
import json

from database.mariadb.models.task_gradio_model import TaskGradio
import logging

logger = logging.getLogger("app")

async def get_video_type(db: Session, task_id: int):
    """
    TaskGradio의 request_body에서 video_type 값을 추출해서 반환
    """
    query = select(TaskGradio).where(TaskGradio.id == task_id)
    result = await db.execute(query)
    task = result.scalars().first()
    
    if not task or not task.request_body:
        return None
    
    try:
        request_data = json.loads(task.request_body)
        
        if "option" in request_data and len(request_data["option"]) > 0:
            video_type = request_data["option"][0].get("video_type")
            return video_type
        else:
            return None
            
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"JSON 파싱 오류: {e}")
        return None