import gradio as gr
from api.modules_gradio.config.constants import APP_DESCRIPTION, ANALYSIS_CODE
from config.const import MODEL

from api.modules_gradio.components.analysis_components import (
    create_analysis_code_dropdown,
    create_llm_model_dropdown,
    create_llm_prompt_textbox
)
from api.modules_gradio.components.image_components import (
    create_user_image_upload,
    create_image_container_and_components
)
from api.modules_gradio.components.output_components import (
    create_request_button,
    create_result_message,
    create_result_json,
    create_result_image,
    create_result_text,
    create_result_video
)
from api.modules_gradio.layout.parameter_layout import (
    create_video_generation_model_dropdown,
    create_wan_parameter_group,
    create_kling_parameter_group
)


def create_main_interface():
    """메인 인터페이스 레이아웃 생성"""
    with gr.Blocks() as demo:
        gr.Markdown(APP_DESCRIPTION)
        with gr.Row():
            with gr.Column():
                with gr.Tab("WAN 모델"):
                    user_image = create_user_image_upload()
                    image_container = create_image_container_and_components()
                    wan_parameter = create_wan_parameter_group()
                    video_generation_model = MODEL.WAN2_2
                with gr.Tab("영상 생성 모델 API"):
                    video_generation_model = create_video_generation_model_dropdown()
                    # user_image = create_user_image_upload()
                    image_container = create_image_container_and_components()
                
                request_button = create_request_button()
            with gr.Column():  
                #요청 결과 메시지
                result_message = create_result_message()

                # 요청 결과 JSON
                result_json = create_result_json()

                # 분석 결과 비디오
                result_video = create_result_video()

    components = {
            'analysis_code': "AI-GRADIO-000001",
            'video_generation_model': video_generation_model,
            'user_image': user_image,
            'image_container': image_container,
            'wan_parameter': wan_parameter,
            'request_button': request_button,
            'result_message' : result_message,
            'result_json' : result_json,
            'result_video': result_video
        }
    return demo, components