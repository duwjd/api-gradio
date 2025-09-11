"""모든 이벤트 핸들러들을 통합 관리"""
from api.modules_gradio.handler.json_handler import setup_json_button_handler
from api.modules_gradio.handler.submit_handler import setup_submit_handler

def setup_all_event_handlers(components):
    """모든 이벤트 핸들러들을 설정하는 메인 함수"""
    
    setup_json_button_handler(components)
    
    # 제출 버튼 핸들러 설정
    setup_submit_handler(components)