from api.modules_gradio.ui_updates import update_video_model_visibility
from api.modules_gradio.handler.submit_handler import setup_submit_handler
def setup_video_handlers(components):
    # """비디오 모델 변경 시 파라미터 그룹 visibility 업데이트 핸들러"""
    # components['video_generation_model'].change(
    #     fn=update_video_model_visibility,
    #     inputs=[components['video_generation_model']],
    #     outputs=[
    #         components['wan_parameter']['group'], 
    #         components['kling_parameter']['group']
    #     ]
    # )
    pass

def setup_submit_handler(components):
    pass
    
    # """제출 버튼 클릭 시 처리 핸들러"""
    # components['submit_btn'].click(
    #     fn=setup_submit_handler.handle_submit,
    #     inputs=[
    #         components['analysis_code'], 
    #         components['user_image'], 
    #         components['video_generation_model'],
    #         components['wan_parameter']['user_prompt_input'], 
    #         components['wan_parameter']['negative_prompt'], 
    #         components['wan_parameter']['total_second_length'], 
    #         components['wan_parameter']['frames_per_second'], 
    #         components['wan_parameter']['num_inference_steps'], 
    #         components['wan_parameter']['guidance_scale'], 
    #         components['wan_parameter']['shift'], 
    #         components['wan_parameter']['seed']
    #     ],
    #     outputs=[components['output']['output']],
    #     show_progress="full"
    # )
