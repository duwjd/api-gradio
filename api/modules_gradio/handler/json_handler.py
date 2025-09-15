import gradio as gr
from utils.generate_request_body import generate_json_i2i, generate_json_i2v
from config.const import I2I_ANALYSIS_CODE, I2V_ANALYSIS_CODE

def setup_json_button_handler(components):
    def handle_i2v_submit(analysis_code, user_image, model_selection, *video_params):
        """Image2Video JSON 생성"""
        # 선택된 모델에 따라 적절한 파라미터만 사용
        video_parameter = {}
        
        # 모델별로 파라미터 인덱스 매핑
        param_index = 0
        if 'i2v_video_parameter' in components:
            # 모든 파라미터 컴포넌트의 값을 수집
            for model_name in ['wan', 'kling', 'seedance']:
                if model_name in components['i2v_video_parameter']:
                    model_params = components['i2v_video_parameter'][model_name]
                    for param_name, _ in model_params.items():
                        if param_name != 'group':
                            # 현재 선택된 모델의 파라미터만 수집
                            if (model_selection in ["WAN2_1", "WAN2_2"] and model_name == 'wan') or \
                               (model_selection == "KLING_V2_1" and model_name == 'kling') or \
                               (model_selection in ["SEEDANCE_1_LITE", "SEEDANCE_1_PRO"] and model_name == 'seedance'):
                                video_parameter[param_name] = video_params[param_index]
                            param_index += 1
        
        # 통합된 component_data 구성
        component_data = {
            'analysis_code': analysis_code,
            'user_image': user_image,
            'model_selection': model_selection,
            'video_parameter': video_parameter
        }
        
        json_result = generate_json_i2v(component_data)
        
        # 성공 메시지와 함께 반환 (outputs에 맞춰 조정)
        return json_result, "JSON 생성 완료", None
    
    def handle_i2i_submit(analysis_code, user_image, model_selection):
        """Image2Image JSON 생성"""
        component_data = {
            'analysis_code': analysis_code,
            'user_image': user_image,
            'model_selection': model_selection
        }
        
        json_result = generate_json_i2i(component_data)
        
        # 성공 메시지와 함께 반환 (outputs에 맞춰 조정)
        return json_result, None  # i2i는 result_message가 없는 것 같으니 None으로
    
    # video_parameter의 개별 컴포넌트들을 inputs 리스트로 생성
    i2v_video_inputs = []
    if 'i2v_video_parameter' in components and isinstance(components['i2v_video_parameter'], dict):
        for model_name in ['wan', 'kling', 'seedance']:
            if model_name in components['i2v_video_parameter']:
                model_params = components['i2v_video_parameter'][model_name]
                for param_name, param_component in model_params.items():
                    if param_name != 'group':  # group은 컴포넌트가 아니므로 제외
                        i2v_video_inputs.append(param_component)
    
    # Image2Video json 버튼
    components['i2v_json_button'].click(
        fn=handle_i2v_submit,
        inputs=[
            components['i2v_analysis_code'],
            components['i2v_input'],
            components['i2v_model_selection']
        ] + i2v_video_inputs,  # 실제 컴포넌트 객체들을 추가
        outputs=[
            components['i2v_output']['result_json'],
            components['i2v_output']['result_message'],
            components['i2v_output']['result_video']
        ]
    )
    
    # Image2Video json 버튼
    components['i2v_json_button'].click(
        fn=handle_i2v_submit,
        inputs=[
            components['i2v_analysis_code'],
            components['i2v_input'],  # 사용자 이미지 입력
            components['i2v_model_selection']
        ] + i2v_video_inputs,  # video parameter 컴포넌트들을 개별적으로 추가
        outputs=[
            components['i2v_output']['result_json'],
            components['i2v_output']['result_message'],
            components['i2v_output']['result_video']
        ]
    )
    
    # Image2Image json 버튼  
    components['i2i_json_button'].click(
        fn=handle_i2i_submit,
        inputs=[
            components['i2i_analysis_code'],
            components['i2i_input'],  # 사용자 이미지 입력
            components['i2i_model_selection']
        ],
        outputs=[
            components['i2i_output']['result_json'], 
            components['i2i_output']['result_image']
        ]
    )