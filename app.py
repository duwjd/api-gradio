import gradio as gr
import json
import generate_json
from const import llm_list
 
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

    



with gr.Blocks() as demo:
    gr.Markdown(
    """
    # gemgem-ai-api test
    * 모든 프로젝트들은 userId=1, projectId=1로 고정됩니다.
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
            user_image = gr.Image(
                label="이미지 업로드", 
                type="filepath",
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

                # 체크박스 상태 변경 시 텍스트박스 가시성 업데이트 함수
                def toggle_prompt_input(is_checked):
                    return gr.update(visible=is_checked)

                # 이벤트 연결
                is_user_prompt_input.change(
                    fn=toggle_prompt_input,
                    inputs=is_user_prompt_input,
                    outputs=user_prompt_input
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

                # 체크박스 상태 변경 시 텍스트박스 가시성 업데이트 함수
                def toggle_prompt_input_kling(is_checked):
                    return gr.update(visible=is_checked)

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

    # Submit 버튼 클릭 시 개별 컴포넌트들을 inputs로 전달
    submit_btn.click(
        fn=generate_json.generate_json,
        inputs=[
            analysis_code, 
            llm_model, 
            user_image, 
            video_generation_model,
            # WAN 파라미터들
            resolution,
            fps,
            duration,
            lora_selection,
            is_user_prompt_input,
            user_prompt_input,
            # Kling 파라미터들
            resolution_kling,
            fps_kling,
            duration_kling,
            is_user_prompt_input_kling,
            user_prompt_input_kling
        ],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch()