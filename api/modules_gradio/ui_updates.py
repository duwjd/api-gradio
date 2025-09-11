import gradio as gr
from PIL import Image
from config.constants import MAX_IMAGES



def update_ui(analysis_code):
    """분석 코드에 따라 UI 컴포넌트들의 가시성을 업데이트하고 이미지 관련 컴포넌트들을 초기화"""
    updates = []
    # 이미지 관련 컴포넌트들 초기화
    if analysis_code in ["AI-ASSIST-000001", "AI-ASSIST-000002"]:
        # image_container 숨기기
        updates.append(gr.update(visible=False))
        
        # image_groups 숨기기 (MAX_IMAGES개)
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False))
        
        # image_previews 초기화 (MAX_IMAGES개)  
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value=None))
        
        # image_choices 초기화 (MAX_IMAGES개)
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value="image"))
        
        # image_prompts 초기화 (MAX_IMAGES개)
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value=""))
    else:
        # AI-PHOTO2VIDEO인 경우 이미지 컴포넌트들은 그대로 유지 (숨김 상태)
        updates.append(gr.update(visible=False))  # image_container
        
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False))  # image_groups
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value=None))  # image_previews
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value="image"))  # image_choices
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value=""))  # image_prompts
    
    return updates


def update_video_model_visibility(model_name):
    """비디오 모델 선택에 따라 파라미터 그룹 가시성 업데이트"""
    if model_name in ["WAN2.1", "WAN2.2"]:
        return gr.update(visible=True), gr.update(visible=False)  # wan_parameter 보이기, kling_parameter 숨기기
    elif model_name == "Kling2.1":
        return gr.update(visible=False), gr.update(visible=True)  # wan_parameter 숨기기, kling_parameter 보이기
    else:
        return gr.update(visible=False), gr.update(visible=False)  # 둘 다 숨기기

def toggle_prompt_input(is_enabled):
    """WAN 모델의 프롬프트 입력 사용 여부에 따라 textbox 토글"""
    return gr.update(visible=is_enabled)

def toggle_prompt_input_kling(is_enabled):
    """Kling 모델의 프롬프트 입력 사용 여부에 따라 textbox 토글"""
    return gr.update(visible=is_enabled)

def update_image_components(files):
    """이미지 업로드 시 이미지 관련 컴포넌트들을 업데이트"""
    updates = []
    
    if not files or len(files) == 0:
        # 이미지가 없으면 모든 컴포넌트 숨기기
        updates.append(gr.update(visible=False))  # image_container
        
        # image_groups 업데이트 (MAX_IMAGES개)
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False))
        
        # image_previews 업데이트 (MAX_IMAGES개)  
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value=None))
        
        # image_choices 업데이트 (MAX_IMAGES개)
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value="image"))
        
        # image_prompts 업데이트 (MAX_IMAGES개)
        for i in range(MAX_IMAGES):
            updates.append(gr.update(visible=False, value=""))
        
        print(f"No images: returning {len(updates)} updates")  # 디버그 로그
        return updates
    
    num_images = len(files)
    print(f"Processing {num_images} images")  # 디버그 로그
    
    # image_container 보이기
    updates.append(gr.update(visible=True))
    print(f"After image_container: {len(updates)} updates")
    
    # image_groups 업데이트 (MAX_IMAGES개)
    for i in range(MAX_IMAGES):
        if i < num_images:
            updates.append(gr.update(visible=True))
        else:
            updates.append(gr.update(visible=False))
    print(f"After image_groups: {len(updates)} updates")
    
    # image_previews 업데이트 (MAX_IMAGES개)
    for i in range(MAX_IMAGES):
        if i < num_images:
            try:
                # 이미지 파일을 PIL Image로 로드
                image = Image.open(files[i].name)
                updates.append(gr.update(visible=True, value=image))
            except Exception as e:
                print(f"Error loading image {i}: {e}")
                updates.append(gr.update(visible=True, value=None))
        else:
            updates.append(gr.update(visible=False, value=None))
    print(f"After image_previews: {len(updates)} updates")
    
    # image_choices 업데이트 (MAX_IMAGES개)
    for i in range(MAX_IMAGES):
        if i < num_images:
            updates.append(gr.update(visible=True, value="image"))
        else:
            updates.append(gr.update(visible=False, value="image"))
    print(f"After image_choices: {len(updates)} updates")
    
    # image_prompts 업데이트 (MAX_IMAGES개) - 처음에는 모두 숨김
    for i in range(MAX_IMAGES):
        if i < num_images:
            updates.append(gr.update(visible=False, value=""))
        else:
            updates.append(gr.update(visible=False, value=""))
    
    print(f"Final: returning {len(updates)} updates")  # 디버그 로그
    return updates

def toggle_image_prompt(choice, image_name):
    if choice == "prompt":
        return gr.update(visible=True, label=f"{image_name}의 프롬프트")
    else:
        return gr.update(visible=False)
    


def update_result_components(analysis_code):
    updates = []
    if "ASSIST" in analysis_code:
        updates.extend([
            gr.update(visible=False, value=None),
            gr.update(visible=False, value=None,),
            gr.update(visible=True)
        ])

    elif analysis_code == "AI-PHOTO2VIDEO-000001":
        updates.extend([
            gr.update(visible=False, value=None, elem_id="result_image"),
            gr.update(visible=True, value=None, elem_id="result_video")
        ])
    return updates
