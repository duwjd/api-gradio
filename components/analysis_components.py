import gradio as gr
from api.modules_gradio.config.constants import ANALYSIS_CODE
from api.modules_gradio.config.models import LLM as llm


llm_list = [llm.GEMINI_2_5_PRO, llm.GPT_4_1, llm.GPT_4_O, llm.GPT_5, llm.GPT_5_NANO, llm.GPT_IMAGE_1, llm.GPT_O_4_MINI]
def create_analysis_code_dropdown():
    """분석 코드 선택 드롭다운 컴포넌트"""
    return gr.Dropdown(
        choices=ANALYSIS_CODE, 
        label="분석 코드 선택",
        visible=True,
        elem_id="analysis_code"
    )

def create_llm_model_dropdown():
    """LLM 모델 선택 드롭다운 컴포넌트"""
    return gr.Dropdown(
        choices=llm_list, 
        label="LLM 모델 선택",
        interactive=True,
        visible=False,
        elem_id="llm_model"
    )

def create_llm_prompt_textbox():
    """LLM 프롬프트 입력 텍스트박스 컴포넌트"""
    return gr.Textbox(
        elem_id="llm_prompt",
        label="LLM 모델 입력 프롬프트",
        placeholder="llm 모델에 입력할 프롬프트를 작성해주세요.",
        interactive=True,
        visible=False
    )