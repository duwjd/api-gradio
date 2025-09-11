import gradio as gr
import asyncio
import json
from api.modules_gradio.ui_updates import update_result_components
from api.modules.analysis.analysis_service import AnalysisService
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger("app")

background_tasks = BackgroundTasks()

def setup_submit_handler(components):
    """분석 요청 제출 버튼 핸들러 설정"""
    
    async def handle_i2v_submit(result_json):
        """Image2Video 제출 버튼 클릭 시 실행"""
        try:
            if not result_json or result_json.strip() == "":
                return "JSON을 먼저 생성해주세요.", "", None
            
            # JSON 문자열을 딕셔너리로 변환
            json_data = json.loads(result_json)
            
            # ReqDoAnalysis 객체 생성
            request_body = ReqDoAnalysis(**json_data)
            
            # 분석 서비스 호출
            result = await AnalysisService().do_analysis(request_body, background_tasks)
            
            # 결과 처리
            if hasattr(result, 'status'):
                status_message = f"상태: {result.status.value if hasattr(result.status, 'value') else result.status}"
                message = result.message if hasattr(result, 'message') else ""
                
                return (
                    f"{status_message}\n{message}",  # result_message
                    result_json,                      # result_json (기존 유지)
                    None                             # result_video (아직 생성되지 않음)
                )
            else:
                return (
                    "분석 요청 실패",
                    result_json,
                    None
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return f"JSON 형식이 올바르지 않습니다: {e}", result_json, None
            
        except Exception as e:
            logger.error(f"분석 요청 중 오류: {e}")
            return f"분석 요청 중 오류가 발생했습니다: {e}", result_json, None

    async def handle_i2i_submit(result_json):
        """Image2Image 제출 버튼 클릭 시 실행"""
        try:
            if not result_json or result_json.strip() == "":
                return "JSON을 먼저 생성해주세요.", None
            
            # JSON 문자열을 딕셔너리로 변환
            json_data = json.loads(result_json)
            
            # ReqDoAnalysis 객체 생성
            request_body = ReqDoAnalysis(**json_data)
            
            # 분석 서비스 호출
            result = await AnalysisService().do_analysis(request_body, background_tasks)
            
            # 결과 처리
            if hasattr(result, 'status'):
                status_message = f"상태: {result.status.value if hasattr(result.status, 'value') else result.status}"
                message = result.message if hasattr(result, 'message') else ""
                
                return (
                    result_json,                      # result_json (기존 유지)
                    None                             # result_image (아직 생성되지 않음)
                )
            else:
                return (
                    result_json,
                    None
                )
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return f"JSON 형식이 올바르지 않습니다: {e}", None
            
        except Exception as e:
            logger.error(f"분석 요청 중 오류: {e}")
            return f"분석 요청 중 오류가 발생했습니다: {e}", None
    
    # Image2Video 제출 버튼 클릭 이벤트 핸들러 설정
    if 'i2v_request_button' in components:
        components['i2v_request_button'].click(
            fn=handle_i2v_submit,
            inputs=[
                components['i2v_output']['result_json']  # 생성된 JSON을 input으로 사용
            ],
            outputs=[
                components['i2v_output']['result_message'], # 처리 결과 메시지
                components['i2v_output']['result_json'],    # JSON (유지)
                components['i2v_output']['result_video']    # 생성된 영상
            ]
        )
    
    # Image2Image 제출 버튼 클릭 이벤트 핸들러 설정  
    if 'i2i_request_button' in components:
        components['i2i_request_button'].click(
            fn=handle_i2i_submit,
            inputs=[
                components['i2i_output']['result_json']  # 생성된 JSON을 input으로 사용
            ],
            outputs=[
                components['i2i_output']['result_json'], # JSON (유지)
                components['i2i_output']['result_image'] # 생성된 이미지
            ]
        )