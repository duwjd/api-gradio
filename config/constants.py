import os
# config/constants.py
"""기존 app.py에서 추출한 모든 상수들"""

# 최대 이미지 개수
MAX_IMAGES = 4

# 분석 코드
ANALYSIS_CODE = "AI-GRADIO-000001"

# 영상 생성 모델 선택지들
VIDEO_MODELS = [
    "WAN2.1", 
    "WAN2.2", 
    "Kling2.1"
]

# 지원되는 이미지 파일 타입들
IMAGE_FILE_TYPES = [
    ".png", 
    ".jpg", 
    ".jpeg", 
    ".webp"
]

# 해상도 선택 옵션들
RESOLUTION_OPTIONS = [
    "480*720", 
    "720*1280"
]

# FPS 선택 옵션들
FPS_OPTIONS = [16, 24, 30]

# LoRA 선택 옵션들
LORA_OPTIONS = [
    "None", 
    "Wan21_CausVid_14B_T2V_lora_rank32.safetensors", 
    "Wan21_CausVid_14B_T2V_lora_rank32_v2.safetensors"
]

# 이미지 선택 옵션들
IMAGE_CHOICE_OPTIONS = ["image", "prompt"]

# WAN 모델 기본값들
WAN_DEFAULT_VALUES = {
    "resolution": "480*720",
    "fps": 24,
    "total_second_length": 2,
    "negative_prompt": "",
    "lora_selection" : "",
    "num_inference_steps": 20,
    "guidance_scale": 5.0,
    "shift": 5.0,
    "seed": 42
}

# Slider 설정값들
SLIDER_CONFIGS = {
    "total_second_length": {"min": 1, "max": 10, "step": 1},
    "num_inference_steps": {"min": 10, "max": 50, "step": 1},
    "guidance_scale": {"min": 1.0, "max": 20.0, "step": 0.1},
    "shift": {"min": 1.0, "max": 10.0, "step": 0.1}
}

# 앱 설명 마크다운
APP_DESCRIPTION = """
# gemgem-ai-api test
* 모든 프로젝트들은 userId=1, projectId=1로 고정됩니다.
"""