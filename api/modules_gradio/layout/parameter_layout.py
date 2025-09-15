"""WAN과 Kling 파라미터 레이아웃 관련 컴포넌트들"""

import gradio as gr
from config.const import (
    VIDEO_MODELS,
    RESOLUTION_OPTIONS, FPS_OPTIONS, LORA_OPTIONS, 
    WAN_DEFAULT_VALUES, SLIDER_CONFIGS
)
from api.modules_gradio.ui_updates import toggle_prompt_input, toggle_prompt_input_kling
from config.const import API_VIDEO_MODEL
from config.const import MODEL

def create_wan_parameter_group():
    """WAN 모델 파라미터 그룹 생성"""
    wan_parameter = gr.Group(elem_id="wan_parameter", visible=True)
    
    with wan_parameter:
        gr.Markdown("#### WAN 모델 파라미터 설정")
        
        with gr.Row():
            with gr.Column():
                is_user_prompt_input = gr.Checkbox(
                    label="wan 모델 사용자 입력 프롬프트 사용 여부", 
                    value=False, 
                    interactive=True
                )

                user_prompt_input = gr.Textbox(
                    elem_classes="model_user_prompt",
                    label="wan모델에 입력하는 프롬프트", 
                    placeholder="wan 모델에 입력하는 프롬프트를 작성해주세요.", 
                    visible=False, 
                    interactive=True
                )
            with gr.Column():
                resolution = gr.Radio(
                choices=RESOLUTION_OPTIONS, 
                value=WAN_DEFAULT_VALUES["resolution"], 
                label="Resolution", 
                interactive=True
            )
        with gr.Row():
            frames_per_second = gr.Radio(
                choices=FPS_OPTIONS, 
                value=WAN_DEFAULT_VALUES["fps"], 
                label="FPS", 
                interactive=True
            )
            total_second_length = gr.Slider(
                minimum=SLIDER_CONFIGS["total_second_length"]["min"], 
                maximum=SLIDER_CONFIGS["total_second_length"]["max"], 
                step=SLIDER_CONFIGS["total_second_length"]["step"], 
                value=WAN_DEFAULT_VALUES["total_second_length"],
                label="Total Second Length",
                interactive=True
            )
            
        with gr.Row():    
            lora_selection = gr.Radio(
                choices=LORA_OPTIONS,
                label="LoRA 선택", 
                interactive=True
            )
            negative_prompt = gr.Textbox(
                label="Negative Prompt",
                value=WAN_DEFAULT_VALUES["negative_prompt"],
                placeholder="negative prompt를 입력하세요",
                interactive=True
            )
        with gr.Row():
            num_inference_steps = gr.Slider(
                minimum=SLIDER_CONFIGS["num_inference_steps"]["min"], 
                maximum=SLIDER_CONFIGS["num_inference_steps"]["max"], 
                step=SLIDER_CONFIGS["num_inference_steps"]["step"], 
                value=WAN_DEFAULT_VALUES["num_inference_steps"],
                label="Num Inference Steps",
                interactive=True
            )
            guidance_scale = gr.Slider(
                    minimum=SLIDER_CONFIGS["guidance_scale"]["min"], 
                    maximum=SLIDER_CONFIGS["guidance_scale"]["max"], 
                    step=SLIDER_CONFIGS["guidance_scale"]["step"], 
                    value=WAN_DEFAULT_VALUES["guidance_scale"],
                    label="Guidance Scale",
                    interactive=True
            )   
        with gr.Row():
            
            shift = gr.Slider(
                minimum=SLIDER_CONFIGS["shift"]["min"], 
                maximum=SLIDER_CONFIGS["shift"]["max"], 
                step=SLIDER_CONFIGS["shift"]["step"], 
                value=WAN_DEFAULT_VALUES["shift"],
                label="Shift",
                interactive=True
            )           
            seed = gr.Number(
                label="Seed",
                value=WAN_DEFAULT_VALUES["seed"],
                interactive=True
            )

        # 이벤트 핸들러 연결
        is_user_prompt_input.change(
            fn=toggle_prompt_input,
            inputs=is_user_prompt_input,
            outputs=user_prompt_input
        )

    return {
        'group': wan_parameter,
        'is_user_prompt_input': is_user_prompt_input,
        'user_prompt_input': user_prompt_input,
        'resolution': resolution,
        'frames_per_second': frames_per_second,
        'total_second_length': total_second_length,
        'lora_selection': lora_selection,
        'negative_prompt': negative_prompt,
        'num_inference_steps': num_inference_steps,
        'guidance_scale': guidance_scale,
        'shift': shift,
        'seed': seed
    }

def create_kling_parameter_group():
    """Kling 모델 파라미터 그룹 생성"""
    kling_parameter = gr.Group(elem_id="kling_parameter", visible=False)
    
    with kling_parameter:
        with gr.Row():
            is_user_prompt_input_kling = gr.Checkbox(
                label="Kling 모델 프롬프트 사용 여부", 
                value=False, 
                interactive=True
            )

        user_prompt_input_kling = gr.Textbox(
            elem_classes="model_user_prompt",
            label="Kling 모델에 입력되는 프롬프트", 
            placeholder="Kling 모델에 입력되는 프롬프트를 작성해주세요.", 
            visible=False, 
            interactive=True
        )                

        # 이벤트 핸들러 연결
        is_user_prompt_input_kling.change(
            fn=toggle_prompt_input_kling,
            inputs=is_user_prompt_input_kling,
            outputs=user_prompt_input_kling
        )
    
    return {
        'group': kling_parameter,
        'is_user_prompt_input_kling': is_user_prompt_input_kling,
        'user_prompt_input_kling': user_prompt_input_kling
    }
    

def create_seedance_parameter_group():
    """Seedance 모델 파라미터 그룹 생성"""
    seedance_parameter = gr.Group(elem_id="seedance_parameter", visible=False)
    
    with seedance_parameter:
        gr.Markdown("#### Seedance 모델 파라미터 설정")
        # Seedance 모델용 파라미터 컴포넌트들
        seedance_option = gr.Radio(
            choices=["Option 1", "Option 2"], 
            value="Option 1", 
            label="Seedance Option", 
            interactive=True
        )
    
    return {
        'group': seedance_parameter,
        'seedance_option': seedance_option
    }


def create_video_generation_model_parameter(model):
    """비디오 생성 모델 파라미터 생성"""
    with gr.Group(visible=False) as wan_parameter:
        gr.Markdown("### WAN 모델 파라미터")
        # WAN 모델용 파라미터 컴포넌트들
        create_wan_parameter_group()

    with gr.Group(visible=False) as kling_parameter:
        gr.Markdown("### KLING 모델 파라미터")
        # KLING 모델용 파라미터 컴포넌트들
        create_kling_parameter_group()

    with gr.Group(visible=False) as seedance_parameter:
        gr.Markdown("### Seedance 모델 파라미터")
        create_seedance_parameter_group()
    # 두 개의 그룹을 리스트로 반환
    return [wan_parameter, kling_parameter, seedance_parameter]