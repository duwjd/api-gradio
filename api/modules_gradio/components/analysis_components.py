import gradio as gr
from config.const import I2V_ANALYSIS_CODE, I2I_ANALYSIS_CODE

def create_analysis_code_dropdown(tab_type):
    """분석 코드 선택 드롭다운 컴포넌트"""
    if tab_type == "image2video":
        selection = I2V_ANALYSIS_CODE
    elif tab_type =="image2image":
        selection = I2I_ANALYSIS_CODE
        
    return gr.Dropdown(
        choices=selection, 
        label="분석 코드 선택",
        visible=True,
        interactive=True,
        elem_id="analysis_code"
    )
def create_generate_json_button(suffix=""):
    """분석 요청 json 생성 버튼"""
    elem_id = f"json_button{suffix}" if suffix else "json_button"
    return gr.Button(
        "분석 요청 json 생성하기",
        interactive=True,
        variant="secondary",
        elem_id=elem_id
    )

def create_request_button():
    """분석 요청 제출 버튼"""
    return gr.Button(
        "분석 요청하기",
        interactive=True,
        variant="primary",
        elem_id = "request_button"
    )