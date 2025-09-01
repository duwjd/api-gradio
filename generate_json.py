import json

def generate_json(analysis_code, llm_model, user_image, video_model, lora_selection, user_prompt):
    """Gradio 입력값들로 JSON 생성"""
    option_list = []
    
    # LLM 모델 추가
    if llm_model:
        option_list.append({
            "src": "llm",
            "type": "model", 
            "value": llm_model
        })
    
    # 이미지 추가
    if user_image:
        option_list.append({
            "src": user_image,
            "type": "image",
            "value": "user_uploaded_image"
        })
    
    # 영상 생성 모델 추가
    if video_model:
        option_list.append({
            "src": "video_generation",
            "type": "model",
            "value": video_model
        })
    
    # Lora 모델 추가
    if lora_selection:
        option_list.append({
            "src": "lora",
            "type": "model", 
            "value": lora_selection
        })
    
    result_json = {
        "userId": 1,
        "projectId": 1,
        "documentS3": ["string"],
        "analysisS3": "string",
        "analysisHttps": "string",
        "group": "string",
        "type": "string",
        "option": option_list,
        "templateCode": analysis_code or "string",
        "chunkData": ["string"],
        "pages": [0],
        "prompt": [user_prompt] if user_prompt else ["string"],
        "inputUrl": "string",
        "inputData": "string",
        "test": {"additionalProp1": {}}
    }
    

    return json.dumps(result_json, indent=2, ensure_ascii=False)