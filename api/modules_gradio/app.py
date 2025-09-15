import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

os.environ['ENV'] = 'gradio'

config_path = os.path.join(project_root, 'config')
print(f"Config path exists: {os.path.exists(config_path)}")

import gradio as gr
from api.modules_gradio.layout.main_layout import create_main_interface
from api.modules_gradio.handler.event_handler import setup_all_event_handlers

# 로깅 설정 추가
from config.log_config import setup_logging
import logging

def main():
    # demo와 components를 받기
    """
    Create a gradio demo interface and set up event handlers for the demo.

    This function creates a gradio interface with components and sets up event handlers
    for the demo by calling `setup_all_event_handlers` inside the demo context.

    Returns
    -------
    demo : gr.Interface
        The created gradio demo interface.
    """
    
    setup_logging("gemgem-ai.log", "error.log")
    logger = logging.getLogger("app")
    logger.info("Gradio 앱 시작 - 로깅 설정 완료")
    logger.info(f"env: {os.getenv('ENV')}")

    demo, components = create_main_interface()
    
    # demo 컨텍스트 안에서 이벤트 핸들러 설정
    with demo:
        setup_all_event_handlers(components)
    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch(
        server_name='0.0.0.0',
        server_port=7861,
        share=True,
        debug=False
    )