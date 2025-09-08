import gradio as gr
import asyncio
import json
from api.modules_gradio.ui_updates import update_result_components
from api.modules_gradio.generate_json import generate_json_wan
from api.modules.analysis.analysis_service import AnalysisService
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from fastapi import BackgroundTasks
from api.modules_gradio.config.constants import ANALYSIS_CODE


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
    async def handle_submit(user_image, user_prompt_input, negative_prompt, 
                           total_second_length, frames_per_second, 
                           num_inference_steps, guidance_scale, shift, seed):
        """제출 버튼 클릭 시 실행"""
        print("[DEBUG] user_image:", type(user_image), user_image)
        request_body = generate_json_wan(
            ANALYSIS_CODE,
            user_image,
            user_prompt_input, 
            negative_prompt, 
            total_second_length, 
            frames_per_second, 
            num_inference_steps, 
            guidance_scale, 
            shift, 
            seed
        )

        # JSON 문자열을 딕셔너리로 변환 후 ReqDoAnalysis 객체 생성
        json_data = json.loads(request_body)
        request_body = ReqDoAnalysis(**json_data)
        
        # 분석 서비스 호출
        result = await AnalysisService().do_analysis(request_body, background_tasks)
        
        # # 결과 처리 - ResDoAnalysis 객체를 적절히 변환
        # if hasattr(result, 'status'):
        #     return (
        #         f"상태: {result.status.value if hasattr(result.status, 'value') else result.status}",
        #         json_string,  # 생성된 JSON
        #         result.message if hasattr(result, 'message') else ""
        #     )
        # else:
        #     return (
        #         "분석 요청 실패",
        #         json_string,
        #         str(result)
        #     )

    
    # 제출 버튼 클릭 이벤트 핸들러 설정
    if 'request_button' in components:
        components['request_button'].click(
            fn=handle_submit,
            inputs=[
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
                components['result_json'] if 'result_json' in components else gr.Code(label="생성된 JSON"),
                components['result_video'] if 'result_video' in components else gr.Video(label="생성된 영상")
            ]
        )
        print("[INFO] 제출 버튼 핸들러 설정 완료")
    else:
        print("[WARNING] request_button 컴포넌트를 찾을 수 없습니다.")