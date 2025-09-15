"""모든 이벤트 핸들러들을 통합 관리"""
from api.modules_gradio.handler.json_handler import setup_json_button_handler
from api.modules_gradio.handler.submit_handler import setup_submit_handler
from api.modules_gradio.handler.model_handler import setup_model_selection_handler
from api.modules_gradio.handler.ui_change_handler import setup_ui_change_handlers

def setup_all_event_handlers(components):
    """모든 이벤트 핸들러들을 설정하는 메인 함수"""
    
    setup_ui_change_handlers(components)

    setup_model_selection_handler(components)

    setup_json_button_handler(components)
    
    # 제출 버튼 핸들러 설정
    setup_submit_handler(components)