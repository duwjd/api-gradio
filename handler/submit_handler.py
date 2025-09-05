import gradio as gr
import asyncio
import json
from api.modules_gradio.ui_updates import update_result_components
from api.modules_gradio.generate_json import generate_json_wan
from api.modules.analysis.analysis_service import AnalysisService
from fastapi import BackgroundTasks


background_tasks = BackgroundTasks()


def extract_text(json_data):
    try:
        # 문자열이면 JSON으로 파싱
        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        # result가 리스트이고 첫 번째에 assist 키가 있으면
        if (
            isinstance(json_data, dict)
            and 'result' in json_data
            and isinstance(json_data['result'], list)
            and len(json_data['result']) > 0
            and 'assist' in json_data['result'][0]
        ):
            return json_data['result'][0]['assist']

        print("[INFO] 'result' 키가 없거나 형식이 올바르지 않음")
        return ""

    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        print(f"[ERROR] JSON 파싱 또는 키 접근 오류: {e}")
        return ""


def extract_video_urls(json_data):
        video_urls = []
        for video in json_data["videos"]:
            video_urls.append(video["url"])
        return video_urls


def setup_submit_handler(components):
    """분석 요청 제출 버튼 핸들러 설정"""

    async def handle_submit():
        request_body = generate_json_wan(components['analysis_code'],
                                         components['wan_parameter']['user_prompt_input'], 
                                         components['wan_parameter']['negative_prompt'], 
                                         components['wan_parameter']['total_second_length'], 
                                         components['wan_parameter']['frames_per_second'], 
                                         components['wan_parameter']['num_inference_steps'], 
                                         components['wan_parameter']['guidance_scale'], 
                                         components['wan_parameter']['shift'], 
                                         components['wan_parameter']['seed'],)
        return await AnalysisService().do_analysis(request_body, background_tasks)

    
    # 제출 버튼 클릭 이벤트 핸들러 설정
    if 'request_button' in components:
        components['request_button'].click(
            fn=handle_submit,
            inputs=[
                components['analysis_code'],
                components['user_image'],
                components['wan_parameter']['user_prompt_input'] if 'wan_parameter' in components else gr.Textbox(value=""),
                components['wan_parameter']['negative_prompt'] if 'wan_parameter' in components else gr.Textbox(value=""),
                components['wan_parameter']['total_second_length'] if 'wan_parameter' in components else gr.Number(value=5),
                components['wan_parameter']['frames_per_second'] if 'wan_parameter' in components else gr.Number(value=24),
                components['wan_parameter']['num_inference_steps'] if 'wan_parameter' in components else gr.Number(value=50),
                components['wan_parameter']['guidance_scale'] if 'wan_parameter' in components else gr.Number(value=5.0),
                components['wan_parameter']['shift'] if 'wan_parameter' in components else gr.Number(value=5.0),
                components['wan_parameter']['seed'] if 'wan_parameter' in components else gr.Number(value=42),
            ],
            outputs=[
                components['result_message'] if 'result_message' in components else gr.Textbox(label="처리 결과"),
                components['result_json'] if 'result_json' in components else gr.Textbox(label="생성된 JSON"),
                components['result_text'] if 'result_text' in components else gr.Textbox(label="생성된 텍스트")
            ]
        )
        print("[INFO] 제출 버튼 핸들러 설정 완료")
    else:
        print("[WARNING] request_button 컴포넌트를 찾을 수 없습니다.")