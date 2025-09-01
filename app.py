import gradio as gr
import json
import generate_json
import uuid

from const import llm_list
from ui_updates import update_ui, update_video_model_visibility, toggle_prompt_input, toggle_prompt_input_kling


with gr.Blocks() as demo:
    gr.Markdown(
    """
    # gemgem-ai-api test
    * 모든 프로젝트들은 userId=1, projectId=1로 고정됩니다.
    * 분석 코드 안내
        - AI-PHOTO2VIDEO-000001: 이미지를 영상으로 변환
        - AI-PHOTO2VIDEO-000002: ???
        - AI-ASSIST-000001: 문장 요약 
        - AI-ASSIST-000002: 맞춤법 검사
    """)
    
    with gr.Row():
        with gr.Column():
            # api 환경 선택
            env = gr.Radio(
                choices=["dev"], 
                label="API 환경 선택",
                value="dev",
                interactive=True
                )

            # 분석 코드 선택
            analysis_code = gr.Dropdown(
                choices=["AI-PHOTO2VIDEO-000001", "AI-PHOTO2VIDEO-000002", "AI-ASSIST-000001", "AI-ASSIST-000002"], 
                label="분석 코드 선택"
            )
            
            # 모든 컴포넌트들을 미리 생성하고 초기에는 숨김
            llm_model = gr.Dropdown(
                choices=llm_list, 
                label="LLM 모델 선택",
                interactive=True,
                visible=False
            )
            
            video_generation_model = gr.Dropdown(
                choices=["WAN2.1", "WAN2.2", "Kling2.1"], 
                label="영상 생성 모델 선택",
                interactive=True,
                visible=False
            )
            user_image = gr.File(
                file_count="multiple",
                file_types=[".png", ".jpg", ".jpeg", ".webp"],
                interactive=True,
                label="이미지 업로드", 
                visible=False
            )

            wan_parameter = gr.Group(visible=False)
            with wan_parameter:
                gr.Markdown("#### WAN 모델 파라미터 설정")
                with gr.Row():
                    resolution=gr.Radio(choices=["480*720", "720*1280"], value="480*720", label="Resolution", interactive=True)
                    fps = gr.Radio(choices=[16, 24, 30], value=24, label="FPS", interactive=True)
                    
                with gr.Row():    
                    duration = gr.Slider(1, 20, step=1, value=5, label="Duration (seconds)", interactive=True)
                    lora_selection = gr.Radio(choices=["None", "Wan21_CausVid_14B_T2V_lora_rank32.safetensors", "Wan21_CausVid_14B_T2V_lora_rank32_v2.safetensors"],label="LoRA 선택", interactive=True)

                with gr.Row():
                    is_user_prompt_input = gr.Checkbox(label="프롬프트 입력 사용하기", value=False, interactive=True)

                # 텍스트박스를 먼저 정의 (초기값은 visible=False)
                user_prompt_input = gr.Textbox(
                    label="사용자 입력 프롬프트", 
                    placeholder="프롬프트를 입력하세요", 
                    visible=False, 
                    interactive=True
                )

            
            kling_parameter = gr.Group(visible=False)
            with kling_parameter:
                gr.Markdown("#### Kling 모델 파라미터 설정")
                with gr.Row():
                    resolution_kling=gr.Radio(choices=["480*720", "720*1280"], value="480*720", label="Resolution", interactive=True)
                    fps_kling = gr.Radio(choices=[16, 24, 30], value=24, label="FPS", interactive=True)
                    
                with gr.Row():    
                    duration_kling = gr.Slider(1, 20, step=1, value=5, label="Duration (seconds)", interactive=True)

                with gr.Row():
                    is_user_prompt_input_kling = gr.Checkbox(label="프롬프트 입력 사용하기", value=False, interactive=True)

                # 텍스트박스를 먼저 정의 (초기값은 visible=False)
                user_prompt_input_kling = gr.Textbox(
                    label="사용자 입력 프롬프트", 
                    placeholder="프롬프트를 입력하세요", 
                    visible=False, 
                    interactive=True
                )                

                # 이벤트 연결
                is_user_prompt_input_kling.change(
                    fn=toggle_prompt_input_kling,
                    inputs=is_user_prompt_input_kling,
                    outputs=user_prompt_input_kling
                )
            
            submit_btn = gr.Button(
                "Submit",
                interactive=True,
                variant="primary"
            )
            

        with gr.Column():
            output = gr.Textbox(
                label="Output",
                placeholder="결과가 여기에 표시됩니다.",
                lines=20
            )
    

    # 분석 코드 선택이 바뀔 때마다 UI 업데이트 (wan_parameter, kling_parameter 추가)
    analysis_code.change(
        fn=update_ui,
        inputs=[analysis_code],
        outputs=[llm_model, user_image, video_generation_model, wan_parameter, kling_parameter]
    )
    
    # 영상 생성 모델이 바뀔 때마다 parameter group 가시성 업데이트
    video_generation_model.change(
        fn=update_video_model_visibility,
        inputs=[video_generation_model],
        outputs=[wan_parameter, kling_parameter]
    )

    is_user_prompt_input.change(
    fn=toggle_prompt_input,
    inputs=is_user_prompt_input,
    outputs=user_prompt_input
    )

    # Submit 버튼 클릭 시 개별 컴포넌트들을 inputs로 전달
    submit_btn.click(
        fn=generate_json.generate_json,
        inputs=[
            analysis_code, 
            llm_model, 
            user_image, 
            video_generation_model
        ],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch()