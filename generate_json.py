import json
import base64
from io import BytesIO
from PIL import Image
import uuid
import os
import tempfile
from utils.s3_util import upload_file

MAX_IMAGES = 10

def generate_json_photo2video(analysis_code, llm_model, user_images, video_generation_model, 
                             user_prompt_input, user_prompt_input_kling, llm_prompt,
                             negative_prompt, total_second_length, frames_per_second, 
                             num_inference_steps, guidance_scale, shift, seed,
                             image_data=None):
    """
    이미지를 영상으로 변환하는 새로운 형식의 JSON을 생성
    image_data: [choice1, choice2, ..., prompt1, prompt2, ...] 형태의 리스트
    """
    try:
        # 기본 JSON 구조
        json_data = {
            "userId": 1,
            "projectId": 1,
            "documentS3": [],
            "analysisS3": "s3://gemgem-public-10k1m/public/local/1/1/analysis/",
            "analysisHttps": "https://gemgem-public-10k1m.s3.ap-northeast-2.amazonaws.com/public/local/1/1/analysis/",
            "group": "10k1m.com",
            "type": analysis_code,
            "option": [],
            "prompt": []
        }
        
        # LLM 프롬프트 추가
        if llm_prompt and llm_prompt.strip():
            json_data["prompt"].append({
                "llmCode": "LLM-CHATGPT",  # 또는 llm_model을 적절히 매핑
                "prompt": llm_prompt.strip()
            })
        
        if not user_images:
            # test 필드는 WAN 모델일 때만 추가
            if video_generation_model and video_generation_model.startswith("WAN"):
                json_data["test"] = {
                    "prompt": user_prompt_input.strip() if user_prompt_input else "",
                    "negative_prompt": negative_prompt if negative_prompt else "테스트",
                    "total_second_length": total_second_length if total_second_length else 2,
                    "frames_per_second": frames_per_second if frames_per_second else 24,
                    "num_inference_steps": num_inference_steps if num_inference_steps else 20,
                    "guidance_scale": guidance_scale if guidance_scale else 5.0,
                    "shift": shift if shift else 5.0,
                    "seed": int(seed) if seed else 42
                }
            return json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # 모든 이미지에 대해 같은 UUID 사용
        file_id = str(uuid.uuid4())
        
        # image_data가 있고 길이가 충분한 경우 (choices + prompts)
        if image_data and len(image_data) >= MAX_IMAGES * 2:
            # 첫 MAX_IMAGES개는 choices, 나머지 MAX_IMAGES개는 prompts
            choices = image_data[:MAX_IMAGES]
            prompts = image_data[MAX_IMAGES:]
            
            # 실제 업로드된 이미지 수만큼 처리
            for i, image_file in enumerate(user_images):
                if i < MAX_IMAGES:
                    choice = choices[i] if i < len(choices) else "image"
                    prompt = prompts[i] if i < len(prompts) else ""
                    s3_url = f"s3://gemgem-public-10k1m/public/local/1/1/document/{file_id}_{i+1:02d}.jpg"
                    json_data["documentS3"].append(s3_url)
                    
                    if choice == "image":
                        json_data["option"].append({
                            "src": s3_url,
                            "type": "image",
                            "value": ""
                        })
                        
                    elif choice == "prompt":
                        json_data["option"].append({
                            "src": s3_url,
                            "type": "prompt",
                            "value": prompt.strip() if prompt else ""
                        })
        else:
            for i, image_file in enumerate(user_images):
                s3_url = f"s3://gemgem-public-10k1m/public/local/1/1/document/{file_id}_{i+1:02d}.jpg"
                json_data["documentS3"].append(s3_url)
                
                json_data["option"].append({
                    "src": s3_url,
                    "type": "image",
                    "value": ""
                })
        
        # test 필드는 WAN 모델일 때만 추가
        if video_generation_model and video_generation_model.startswith("WAN"):
            json_data["test"] = {
                "prompt": user_prompt_input.strip() if user_prompt_input else "",
                "negative_prompt": negative_prompt if negative_prompt else "테스트",
                "total_second_length": total_second_length if total_second_length else 2,
                "frames_per_second": frames_per_second if frames_per_second else 24,
                "num_inference_steps": num_inference_steps if num_inference_steps else 20,
                "guidance_scale": guidance_scale if guidance_scale else 5.0,
                "shift": shift if shift else 5.0,
                "seed": int(seed) if seed else 42
            }
        
        # S3에 이미지 업로드
        for i in range(len(json_data["documentS3"])):
            upload_file(user_images[i], json_data["documentS3"][i])

        # JSON 문자열로 변환 (수정된 부분: 튜플이 아닌 문자열만 반환)
        json_string = json.dumps(json_data, indent=2, ensure_ascii=False)   
        
        return json_string  # 튜플이 아닌 문자열만 반환
        
    except Exception as e:
        # 에러 발생 시 기본 구조에 맞춘 JSON 반환
        error_json = {
            "userId": 1,
            "projectId": 1,
            "documentS3": [],
            "analysisS3": "s3://gemgem-public-10k1m/public/local/1/1/analysis/",
            "analysisHttps": "https://gemgem-public-10k1m.s3.ap-northeast-2.amazonaws.com/public/local/1/1/analysis/",
            "group": "10k1m.com",
            "type": analysis_code if analysis_code else "AI-GRADIO-000001",
            "option": [],
            "prompt": [],
            "error": str(e)  # 에러는 별도 필드로 추가
        }
        return json.dumps(error_json, indent=2, ensure_ascii=False)

def generate_json_ai_assist(analysis_code, llm_model, llm_prompt):
    """
    AI 어시스트 기능을 위한 JSON 생성 (기존과 동일)
    """
    try:
        json_data = {
            "userId" : 1,
            "projectId" : 1,
            "type": analysis_code,
            "inputData": llm_prompt
        }
        
        json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
        return json_string
        
    except Exception as e:
        # AI 어시스트용 에러 JSON
        error_json = {
            "userId": 1,
            "projectId": 1,
            "type": analysis_code if analysis_code else "AI-ASSIST-000001",
            "inputData": "",
            "error": str(e)
        }
        return json.dumps(error_json, indent=2, ensure_ascii=False)
    
def generate_json_wan(analysis_code, user_image, user_prompt_input, negative_prompt, total_second_length, fps, num_inference_steps, guidance_scale, shift, seed):
    """
    WAN 모델을 위한 JSON 생성 (이미지 한 장 업로드)
    """
    try:
        # 입력 검증
        if not user_image:
            raise ValueError("이미지가 제공되지 않았습니다.")
            
        if not os.path.exists(user_image):
            raise ValueError(f"이미지 파일을 찾을 수 없습니다: {user_image}")
        
        
        # if user_image is None:
        #     raise ValueError("이미지가 제공되지 않았습니다.")

        # if isinstance(user_image, Image.Image):
        #     # PIL 이미지를 임시 파일로 저장
        #     tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        #     user_image.save(tmp_file.name)
        #     user_image_path = tmp_file.name
        # elif isinstance(user_image, str) and os.path.exists(user_image):
        #     # 파일 경로로 들어온 경우
        #     user_image_path = user_image
        # else:
        #     raise ValueError("유효하지 않은 이미지 입력입니다.")

        # UUID를 사용해서 파일 ID 생성
        file_id = str(uuid.uuid4())
        
        # S3 URL 생성 (이미지 한 장)
        s3_url = f"s3://gemgem-public-10k1m/public/local/1/1/document/{file_id}_01.jpg"
        
        json_data = {
            "userId": 1,
            "projectId": 1,
            "documentS3": [s3_url],
            "analysisS3": "s3://gemgem-public-10k1m/public/local/1/1/analysis/",
            "analysisHttps": "https://gemgem-public-10k1m.s3.ap-northeast-2.amazonaws.com/public/local/1/1/analysis/",
            "group": "10k1m.com",
            "type": analysis_code,
            "option": [{
                "src": s3_url,
                "type": "image",
                "value": ""
            }],
            "prompt": [
                {
                    "llmCode": "LLM-CHATGPT",
                    "prompt": ""
                }
            ],
            "test": {
                "prompt": user_prompt_input or "",
                "negative_prompt": negative_prompt or "",
                "total_second_length": total_second_length or 5,
                "frames_per_second": fps or 24,
                "num_inference_steps": num_inference_steps or 50,
                "guidance_scale": guidance_scale or 5.0,
                "shift": shift or 5.0,
                "seed": int(seed) if seed else 42
            }
        }
        
        # S3에 이미지 업로드 시도
        try:
            upload_success = upload_file(user_image, s3_url)
            if not upload_success:
                print(f"[WARNING] S3 업로드 실패: {s3_url}")
        except Exception as upload_error:
            print(f"[ERROR] S3 업로드 중 오류: {upload_error}")
            # 업로드 실패해도 JSON은 반환 (로컬 테스트 환경 등을 위해)
        
        # JSON 문자열로 변환
        json_string = json.dumps(json_data, indent=2, ensure_ascii=False)
        print(f"[INFO] Generated JSON: {json_string}")
        return json_string
        
    except Exception as e:
        print(f"[ERROR] generate_json_wan 오류: {e}")
        # 에러 발생 시 기본 구조에 맞춘 JSON 반환
        error_json = {
            "userId": 1,
            "projectId": 1,
            "documentS3": [],
            "analysisS3": "s3://gemgem-public-10k1m/public/local/1/1/analysis/",
            "analysisHttps": "https://gemgem-public-10k1m.s3.ap-northeast-2.amazonaws.com/public/local/1/1/analysis/",
            "group": "10k1m.com",
            "type": analysis_code if analysis_code else "AI-GRADIO-000001",
            "option": [],
            "prompt": [
                {
                    "llmCode": "LLM-CHATGPT",
                    "prompt": ""
                }
            ],
            "error": str(e)  # 에러는 별도 필드로 추가
        }
        return json.dumps(error_json, indent=2, ensure_ascii=False)