import json
import pydantic


def generate_json(analysis_code, llm_model, user_image, video_generation_model):
    option_list = []
    
    # 이미지 추가
    if user_image:
        option_list.append({
            "src": user_image,
            "type": "image",
            "value": ""
        })
    
    # 영상 생성 모델 추가
    if video_generation_model:
        option_list.append({
            "src": "video_generation",
            "type": "model",
            "value": video_generation_model
        })
    
    # 프롬프트가 없으면 기본값 사용
    if not prompt_list:
        prompt_list = ["string"]
    
    result_json = {
        "userId": 1,
        "projectId": 1,
        "group": "10k1m.com",
        "type": analysis_code,
        "documentS3": ["string"],
        "analysisS3": "s3://gemgem-private-10k1m/private/development/1/1/analysis/",
        "analysisHttps": "https://cdn.gemgem.video/private/development/1/1/analysis/", 
        "option": option_list,
        "templateCode": analysis_code or "string",
        "chunkData": ["string"],
        "pages": [0],
        "prompt": prompt_list,
        "inputUrl": "string",
        "inputData": "string",
        "test": {"additionalProp1": {}}
    }
    
    return json.dumps(result_json, indent=2, ensure_ascii=False)