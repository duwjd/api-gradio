import gradio as gr

def update_ui(analysis_code):
    """분석 코드 선택에 따라 UI 컴포넌트들의 visibility를 업데이트"""
    if analysis_code in ["AI-PHOTO2VIDEO-000001", "AI-PHOTO2VIDEO-000002"]:
        return [
            gr.update(visible=True),   # llm_model
            gr.update(visible=True),   # user_image
            gr.update(visible=True),   # video_generation_model
            gr.update(visible=False),  # wan_parameter (초기화)
            gr.update(visible=False),  # kling_parameter (초기화)
        ]
    elif analysis_code in ["AI-ASSIST-000001", "AI-ASSIST-000002"]:
        return [
            gr.update(visible=True),   # llm_model
            gr.update(visible=False),  # user_image (숨김)
            gr.update(visible=False),  # video_generation_model (숨김)
            gr.update(visible=False),  # wan_parameter (숨김)
            gr.update(visible=False),  # kling_parameter (숨김)
        ]

def update_video_model_visibility(video_model):
    if video_model and video_model.startswith("WAN"):
        return gr.update(visible=True), gr.update(visible=False)
    elif video_model and video_model.startswith("Kling"):
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=False), gr.update(visible=False)

# 체크박스 상태 변경 시 텍스트박스 가시성 업데이트 함수
def toggle_prompt_input(is_checked):
    return gr.update(visible=is_checked)

def toggle_prompt_input_kling(is_checked):
    return gr.update(visible=is_checked)