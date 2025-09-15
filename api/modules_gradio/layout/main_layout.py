import gradio as gr
from api.modules_gradio.components.analysis_components import (
    create_analysis_code_dropdown,
    create_generate_json_button,
    create_request_button
)
from api.modules_gradio.components.input_components import(
    create_input
)
from api.modules_gradio.components.output_components import (
    create_output
)

from api.modules_gradio.components.model_components import(
    create_video_generation_model_dropdown,
    create_image_generation_model_dropdown
)
from api.modules_gradio.layout.parameter_layout import(
    create_video_generation_model_parameter
)

def create_main_interface():
    """메인 인터페이스 레이아웃 생성"""
    with gr.Blocks() as demo:
        gr.Markdown("# GEMGEM-AI-TEST")
        
        # Image2Video 탭
        with gr.Tab("Image2Video", id="tab_image2video"):
            with gr.Row():
                with gr.Column():
                    i2v_analysis_code = create_analysis_code_dropdown("image2video")
                    i2v_input = create_input("image2video")
                    i2v_model_selection = create_video_generation_model_dropdown()
                    model = "WAN"
                    i2v_video_parameter = create_video_generation_model_parameter(model)
                    i2v_generate_json_button = create_generate_json_button("_i2v")
                    i2v_request_button = create_request_button()
                with gr.Column():
                    i2v_output = create_output("image2video")
                    
        # Image2Image 탭        
        with gr.Tab("Image2Image", id="tab_image2image"):
            with gr.Row():
                with gr.Column():
                    i2i_analysis_code = create_analysis_code_dropdown("image2image")
                    i2i_input = create_input("image2image")
                    i2i_model_selection = create_image_generation_model_dropdown()
                    i2i_generate_json_button = create_generate_json_button("_i2i")
                    i2i_request_button = create_request_button()
                with gr.Column():
                    i2i_output = create_output("image2image")

    # components 딕셔너리 수정
    components = {
        'i2v_analysis_code': i2v_analysis_code,
        'i2v_input': i2v_input,
        'i2v_video_parameter': i2v_video_parameter,  # 전체 딕셔너리 저장
        'i2v_model_selection': i2v_model_selection,
        'i2v_json_button': i2v_generate_json_button,
        'i2v_request_button': i2v_request_button,
        'i2v_output': i2v_output,
        
        'i2i_analysis_code': i2i_analysis_code,
        'i2i_input': i2i_input,
        'i2i_model_selection': i2i_model_selection,
        'i2i_json_button': i2i_generate_json_button,
        'i2i_request_button': i2i_request_button,
        'i2i_output': i2i_output,
    }

    # video_parameter 개별 컴포넌트들만 추가
    if isinstance(i2v_video_parameter, dict):
        for model_name, model_params in i2v_video_parameter.items():
            if isinstance(model_params, dict):
                for param_name, param_component in model_params.items():
                    # group은 제외하고 실제 컴포넌트만 추가
                    if param_name != 'group':
                        components[f'i2v_{model_name}_{param_name}'] = param_component
    
    return demo, components