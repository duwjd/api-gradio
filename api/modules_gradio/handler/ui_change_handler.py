import gradio as gr
from PIL import Image
from config.const import MAX_IMAGES
from config.const import MODEL


def setup_ui_change_handlers(components):
    def update_video_model_visibility(model_name):
        """비디오 모델 선택에 따라 파라미터 그룹 가시성 업데이트"""
        if model_name in "WAN2_1" or model_name == "WAN2_2":
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
        elif model_name == "Kling":
            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)
        elif model_name == "Seedance":
            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
        else:
            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

    def toggle_prompt_input(is_enabled):
        """WAN 모델의 프롬프트 입력 사용 여부에 따라 textbox 토글"""
        return gr.update(visible=is_enabled)

    def toggle_prompt_input_kling(is_enabled):
        """Kling 모델의 프롬프트 입력 사용 여부에 따라 textbox 토글"""
        return gr.update(visible=is_enabled)