"""출력 관련 컴포넌트들"""
import gradio as gr

def create_result_message():
    """분석 요청 결과 메시지"""
    return gr.Textbox(
        label="분석 요청 결과 메시지",
        visible=True,
        elem_id="result_message"
    )

def create_result_json():
    """분석 요청 JSON"""
    return gr.Code(
        label="분석 요청 JSON",
        visible=True,
        elem_id="result_json"
    )

def create_result_video():
    """분석 결과 영상"""
    return gr.Video(
        label="분석 결과 영상",
        visible=True,
        elem_id="result_video"
    )

def create_result_text():
    """분석 결과 텍스트""" 
    return gr.Textbox(
        label="분석 결과 텍스트",
        visible=True,
        elem_id="result_text"
    )

def create_result_image():
    """분석 결과 이미지"""
    return gr.Image(
        label="분석 결과 이미지",
        visible=True,
        elem_id="result_image"
    )
    
    
def create_output(tab_type):
    if tab_type == "image2video":
        result_json = create_result_json()
        result_message = create_result_message()
        result_video = create_result_video()
        return {
            'result_json': result_json,
            'result_message': result_message,
            'result_video': result_video
        }
    elif tab_type == "image2image":
        result_json = create_result_json()
        result_message = create_result_message()
        result_image = create_result_image()
        return {
            'result_json': result_json,
            'result_message': result_message,
            'result_image': result_image
        }