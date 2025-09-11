import gradio as gr
from config.constants import I2V_ANALYSIS_CODE, I2I_ANALYSIS_CODE
from config.models import LLM as llm
from config.const import API_VIDEO_MODEL

def create_llm_model_dropdown():
    """LLM 모델 선택 드롭다운 컴포넌트"""
    return gr.Dropdown(
        choices=["Claude, ChatGPT, Gemini"], 
        label="LLM 모델 선택",
        interactive=True,
        visible=False,
        elem_id="llm_model"
    )
    

def create_image_generation_model_dropdown():
    return gr.Dropdown(
        choices = ["ChatGPT"],
        label="이미지 생성 모델 선택",
        interactive=True,
        visible=True,
        elem_id = "select_image_generation_model"
    )


def create_video_generation_model_dropdown():
    """비디오 생성 모델 선택 드롭다운"""
    return gr.Dropdown(
        choices=[API_VIDEO_MODEL.HAILUO_02, API_VIDEO_MODEL.KLING_V2_1, API_VIDEO_MODEL.SEEDANCE_1_LITE, API_VIDEO_MODEL.SEEDANCE_1_PRO, "WAN2.2"], 
        label="영상 생성 모델 선택",
        interactive=True,
        visible=True,
        elem_id="select_video_generation_model"
    )