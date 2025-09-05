# handlers/image_handler.py
"""이미지 관련 이벤트 핸들러"""

from api.modules_gradio.ui_updates import update_image_components

def setup_image_handlers(components):
    """이미지 업로드 변경 시 미리보기 업데이트 핸들러"""
    components['user_image'].change(
        fn=update_image_components,
        inputs=[components['user_image']],
        outputs=[
            components['image_container']['container']
        ] + 
        components['image_container']['groups'] + 
        components['image_container']['previews'] + 
        components['image_container']['choices'] + 
        components['image_container']['prompts']
    )