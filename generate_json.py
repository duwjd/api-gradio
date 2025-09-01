import json
import uuid
import os


def generate_json(analysis_code, llm_model, user_image, video_generation_model):
    option_list = []
    document_s3_list = []
    
    # 여러 이미지 처리
    if user_image:
        # user_image가 리스트인지 확인 (Gradio file_count="multiple"의 경우)
        image_list = user_image if isinstance(user_image, list) else [user_image]
        # UUID4 생성
        unique_id = str(uuid.uuid4())
        for idx, image_file in enumerate(image_list, 1):
            if image_file:  # 파일이 존재하는 경우                
                # 원본 파일의 확장자 추출
                if hasattr(image_file, 'name'):
                    original_name = image_file.name
                elif isinstance(image_file, str):
                    original_name = image_file
                else:
                    original_name = f"image_{idx}.jpeg"
                
                file_extension = os.path.splitext(original_name)[1] or '.jpeg'
                
                # S3 경로 생성 (UUID + 순서번호 + 확장자)
                s3_filename = f"{unique_id}_{idx:02d}{file_extension}"
                s3_path = f"s3://gemgem-private-10k1m/private/development/1/1/document/{s3_filename}"
                
                # documentS3 리스트에 추가
                document_s3_list.append(s3_path)
                
                # option 리스트에 추가
                option_list.append({
                    "src": s3_path,
                    "type": "image",
                    "value": ""
                })
    
    result_json = {
        "userId": 1,
        "projectId": 1,
        "group": "10k1m.com",
        "type": analysis_code,
        "documentS3": document_s3_list,
        "analysisS3": "s3://gemgem-private-10k1m/private/development/1/1/analysis/",
        "analysisHttps": "https://cdn.gemgem.video/private/development/1/1/analysis/", 
        "option": option_list,
    }
    
    return json.dumps(result_json, indent=2, ensure_ascii=False)