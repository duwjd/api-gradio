import gradio as gr

def create_user_image_upload():
    """이미지 파일 업로드 컴포넌트"""
    return gr.Image(
        elem_id="user_image_upload",
        type="filepath",
        sources=["upload"],
        label="이미지 업로드",
        interactive=True
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
    
def create_input(tab_type):
    """사용자 입력 컴포넌트 생성"""
    if tab_type == "image2video":
        return create_user_image_upload()
    elif tab_type == "image2image":
        return create_user_image_upload()