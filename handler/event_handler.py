"""모든 이벤트 핸들러들을 통합 관리"""

from api.modules_gradio.handler.image_handler import setup_image_handlers
from api.modules_gradio.handler.video_handler import setup_video_handlers
from api.modules_gradio.handler.submit_handler import setup_submit_handler

def setup_all_event_handlers(components):
    """모든 이벤트 핸들러들을 설정하는 메인 함수"""
    
    # 분석 관련 핸들러 설정
    # setup_analysis_handlers(components)
    
    # 이미지 관련 핸들러 설정
    setup_image_handlers(components)
    
    # 비디오 관련 핸들러 설정
    setup_video_handlers(components)
    
    # 제출 버튼 핸들러 설정
    setup_submit_handler(components)