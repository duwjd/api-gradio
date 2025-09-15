import gradio as gr

from api.modules_gradio.handler.submit_handler import setup_submit_handler
from api.modules_gradio.handler.json_handler import setup_json_button_handler
from api.modules_gradio.ui_updates import update_video_model_visibility

def setup_model_selection_handler(components):
    """모델 선택 드롭다운 변경 이벤트 핸들러 설정"""
    i2v_model_selection = components['i2v_model_selection']
    i2v_video_parameter = components['i2v_video_parameter']
    
    def update_model(model_name):
        """모델 선택에 따라 파라미터 그룹 가시성 업데이트"""
        wan_param_update, kling_param_update = update_video_model_visibility(model_name)
        return wan_param_update, kling_param_update, model_name, gr.update(value=model_name)
    
    i2v_model_selection.change(
        fn=update_model,
        inputs=i2v_model_selection,
        outputs=[i2v_video_parameter[0], i2v_video_parameter[1], i2v_video_parameter[2]],
    )