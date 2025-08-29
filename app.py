import gradio as gr

def update_ui(analysis_code):
    """분석 코드 선택에 따라 UI 컴포넌트들의 visibility를 업데이트"""
    if analysis_code in ["AI-PHOTO2VIDEO-000001", "AI-PHOTO2VIDEO-000002"]:
        return [
            gr.update(visible=True),   # llm_model
            gr.update(visible=True),   # user_image
            gr.update(visible=True),   # video_generation_model
            gr.update(visible=False),  # user_video (숨김)
        ]
    elif analysis_code in ["AI-ASSIST-000001", "AI-ASSIST-000002"]:
        return [
            gr.update(visible=True),   # llm_model
            gr.update(visible=False),  # user_image (숨김)
            gr.update(visible=False),  # video_generation_model (숨김)
            gr.update(visible=True),   # user_video
        ]
    else:
        return [
            gr.update(visible=False),  # llm_model (숨김)
            gr.update(visible=False),  # user_image (숨김)
            gr.update(visible=False),  # video_generation_model (숨김)
            gr.update(visible=False),  # user_video (숨김)
        ]

with gr.Blocks() as demo:
    gr.Markdown(
    """
    # gemgem-ai-api test
    """)
    
    with gr.Row():
        with gr.Column():
            # 분석 코드 선택
            analysis_code = gr.Dropdown(
                choices=["AI-PHOTO2VIDEO-000001", "AI-PHOTO2VIDEO-000002", "AI-ASSIST-000001", "AI-ASSIST-000002"], 
                label="분석 코드 선택"
            )
            
            # 모든 컴포넌트들을 미리 생성하고 초기에는 숨김
            llm_model = gr.Dropdown(
                choices=["gpt-3.5-turbo", "gpt-4"], 
                label="LLM 모델 선택",
                visible=False
            )
            
            user_image = gr.Image(
                label="이미지 업로드", 
                type="filepath",
                visible=False
            )
            
            video_generation_model = gr.Dropdown(
                choices=["WAN2.1", "WAN2.2", "Kling2.1"], 
                label="영상 생성 모델 선택",
                visible=False
            )
            
            # user_video = gr.Video(
            #     label="비디오 업로드", 
            #     type="filepath",
            #     visible=False
            # )
            
            user_prompt_input = gr.Textbox(
                placeholder="사용자 프롬프트를 입력하세요.",
                label="사용자 프롬프트"
            )
            
            submit_btn = gr.Button("Submit")
    
    # 분석 코드 선택이 바뀔 때마다 UI 업데이트
    analysis_code.change(
        fn=update_ui,
        inputs=[analysis_code],
        outputs=[llm_model, user_image, video_generation_model]
    )

if __name__ == "__main__":
    demo.launch()