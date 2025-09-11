import gradio as gr
from utils.generate_json import generate_json_i2i, generate_json_i2v
from config.constants import I2I_ANALYSIS_CODE, I2V_ANALYSIS_CODE

def setup_json_button_handler(components):
    
    def handle_i2v_submit(analysis_code, user_image, model_selection, *video_params):
        """Image2Video JSON 생성"""
        # video_params를 딕셔너리로 변환
        video_parameter = {}
        if 'i2v_video_parameter' in components and isinstance(components['i2v_video_parameter'], dict):
            # 딕셔너리의 키 순서대로 값들을 매핑
            param_keys = [k for k in components['i2v_video_parameter'].keys() if k != 'group']
            for i, value in enumerate(video_params):
                if i < len(param_keys):
                    video_parameter[param_keys[i]] = value
        
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
        for key, component in components['i2v_video_parameter'].items():
            if key != 'group':  # 'group'은 실제 input 컴포넌트가 아니므로 제외
                i2v_video_inputs.append(component)
    
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