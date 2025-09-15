import gradio as gr
from PIL import Image
from config.const import MAX_IMAGES
from config.const import MODEL

def update_video_model_visibility(model_name):
    """비디오 모델 선택에 따라 파라미터 그룹 가시성 업데이트"""
    if model_name in ["WAN2_1", "WAN2_2"]:
        return gr.update(visible=True), gr.update(visible=False)  # wan_parameter 보이기, kling_parameter 숨기기
    elif model_name == "KLING_V2_1":
        return gr.update(visible=False), gr.update(visible=True)  # wan_parameter 숨기기, kling_parameter 보이기
    elif model_name in ["SEEDANCE_1_LITE", "SEEDANCE_1_PRO"]:
        return gr.update(visible=False), gr.update(visible=False)  # 둘 다 숨기기
    else:
        return gr.update(visible=False), gr.update(visible=False)  # 둘 다 숨기기

def toggle_prompt_input(is_enabled):
    """WAN 모델의 프롬프트 입력 사용 여부에 따라 textbox 토글"""
    return gr.update(visible=is_enabled)

def toggle_prompt_input_kling(is_enabled):
    """Kling 모델의 프롬프트 입력 사용 여부에 따라 textbox 토글"""
    return gr.update(visible=is_enabled)