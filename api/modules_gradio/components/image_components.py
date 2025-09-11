# import gradio as gr
# from api.modules_gradio.config.constants import MAX_IMAGES, IMAGE_CHOICE_OPTIONS
# from api.modules_gradio.ui_updates import toggle_image_prompt



# def create_image_container_and_components():
#     """이미지 컨테이너와 모든 관련 컴포넌트들을 생성"""
#     image_container = gr.Group(visible=False, elem_id="image_container")
    
#     image_previews = []
#     image_choices = []
#     image_prompts = []
#     image_groups = []
    
#     with image_container:
#         gr.Markdown("### 첨부한 이미지")
#         for i in range(MAX_IMAGES):
#             with gr.Group(visible=True, elem_id=f"image_group_{i}") as img_group:
#                 with gr.Row():
#                     with gr.Column(scale=1):
#                         img_preview = gr.Image(
#                             label=f"이미지 {i+1}",
#                             interactive=False,
#                             visible=True,
#                             elem_id=f"image_preview_{i}",
#                             height=200,
#                             width=200
#                         )
#                         image_previews.append(img_preview)
                    
#                     with gr.Column(scale=2):
#                         img_choice = gr.Radio(
#                             choices=IMAGE_CHOICE_OPTIONS,
#                             value="image",
#                             label="이미지의 영상 생성 옵션",
#                             visible=False,
#                             elem_id=f"image_choice_{i}"
#                         )
#                         image_choices.append(img_choice)
                        
#                         # 이미지 프롬프트 textbox
#                         img_prompt = gr.Textbox(
#                             label=f"이미지 {i+1}의 프롬프트",
#                             placeholder="각 이미지에 대한 프롬프트를 입력해주세요.",
#                             visible=False,
#                             interactive=True,
#                             elem_id=f"image_prompt_{i}"
#                         )
#                         image_prompts.append(img_prompt)
                        
#                         # 기존 이벤트 핸들러 연결
#                         img_choice.change(
#                             fn=lambda choice, idx=i: toggle_image_prompt(choice, f"이미지 {idx+1}"),
#                             inputs=[img_choice],
#                             outputs=[img_prompt]
#                         )
#             image_groups.append(img_group)
    
#     return {
#         'container': image_container,
#         'previews': image_previews,
#         'choices': image_choices,
#         'prompts': image_prompts,
#         'groups': image_groups
#     }