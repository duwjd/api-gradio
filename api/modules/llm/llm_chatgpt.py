import asyncio
import base64
import json
import logging
import os
import shutil
from typing import List, Optional

import openai
from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_task_llm_dao import update_task_llm_progress
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from api.modules.llm.llm_util import update_progress_background
from api.modules.llm.schema.llm_chatgpt_schema import (
    GPTContext2ScriptList,
    GPTContext2Video,
    GPTContext2VideoList,
    GPTImage2ContextList,
    GPTOutput,
    GPTOutput_OCR_Ratio,
    GPTPhoto2MusicOutput,
    GPTPhoto2VideoCategoryOutput,
    GPTPhoto2VideoOutput,
    GPTPhoto2VideoOutputs,
    GPTGps2KeywordList

)
from api.modules.llm.schema.llm_schema import ReqDoLLM, ReqLLMAssist
from config.const import ANALYSIS_ERROR, S3
from config.llm_const import LLM, LLMConfig
# from utils.chatgpt_util_engine import chatgpt_client
from utils.s3_util_engine import get_s3_bucket, upload_s3_binary
from utils.util import (
    download_and_encode_image,
    encode_file_base64,
    get_extension,
    get_mime_type,
)

logger = logging.getLogger("app")


# async def chatgpt_analysis_engine(req_body: ReqDoLLM, db: Session) -> str:
#     """
#     텍스트, 파일을 입력 받아 ChatGpt API를 통해 텍스트 분석 및 요약을 수행하는 함수.

#     Args:
#         req_body (ReqDoLLM) 분석 req_body
#         db (Session): db 세션

#     Returns:
#         str: ChatGpt API에서 생성된 텍스트 출력.
#     """
#     try:
#         input_data = req_body.inputData
#         prompt = req_body.prompt
#         system_prompt = req_body.systemPrompt

#         client = chatgpt_client()
#         type = req_body.type
#         tmp_file_path = None
#         mime_type = get_mime_type(input_data)

#         if type == "text":
#             content = input_data
#             # 메시지 구성
#             messages = (
#                 [{"role": "system", "content": system_prompt}] if system_prompt else []
#             ) + [
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": content},
#             ]
#         elif type == "file":

#             if mime_type.startswith("image/"):
#                 # 이미지 파일 처리
#                 base64_image = await download_and_encode_image(mime_type, input_data)
#                 messages = (
#                     [{"role": "system", "content": system_prompt}]
#                     if system_prompt
#                     else []
#                 )
#                 messages = messages + [
#                     {
#                         "role": "user",
#                         "content": [
#                             {"type": "text", "text": prompt},
#                             {
#                                 "type": "image_url",
#                                 "image_url": {"url": base64_image},
#                             },
#                         ],
#                     }
#                 ]

#             elif mime_type == "application/pdf":
#                 # PDF 파일 처리
#                 base64_images = await download_and_encode_image(mime_type, input_data)
#                 base64_blocks = [
#                     {"type": "image_url", "image_url": {"url": base64_image}}
#                     for base64_image in base64_images
#                 ]
#                 messages = (
#                     [{"role": "system", "content": system_prompt}]
#                     if system_prompt
#                     else []
#                 )

#                 messages = messages + [
#                     {
#                         "role": "user",
#                         "content": [{"type": "text", "text": prompt}, *base64_blocks],
#                     }
#                 ]

#             else:
#                 raise ValueError(f"지원하지 않는 타입 입니다. type:{type}")

#         # # progres 백그라운드 task 처리
#         # progress_event = asyncio.Event()
#         # progress_task = asyncio.create_task(
#         #     update_progress_background(req_body, db, progress_event)
#         # )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             reasoning_effort="low",
#             response_format=GPTOutput,
#         )

#         result = [
#             scene.model_dump() for scene in response.choices[0].message.parsed.scenes
#         ]

#         logger.info(response.usage)
#         logger.info(result)

#         return result
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#     finally:
#         if tmp_file_path:

#             shutil.rmtree(tmp_file_path)

#         # progres 백그라운드 task 종료

#         # progress_event.set()
#         # await progress_task


# async def chatgpt_doc_parser_image(
#     req_body: ReqDoAnalysis,
#     images: list,
#     prompt: str,
#     sys_instruct: Optional[str] = None,
#     small_images: list = [],
#     db: Session = None,
# ):
#     try:
#         # AI-ANALYSIS-000001

#         logger.info("[LLM-CHATGPT] doc parser image llm 요청")
#         client = chatgpt_client()
#         mime_type = "image/jpeg"

#         docs = [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await download_and_encode_image(mime_type, image)},
#             }
#             for image in images
#         ]
#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []

#         extra_data = []
#         if len(small_images):
#             extra_data.append({"type": "text", "text": "LIST OF SMALL IMAGES"})
#             extra_data.extend(
#                 [
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": await download_and_encode_image(
#                                 mime_type, small_image
#                             )
#                         },
#                     }
#                     for small_image in small_images
#                 ]
#             )

#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": prompt}, *docs, *extra_data],
#             }
#         ]
#         # progres 백그라운드 task 처리
#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(req_body, db, progress_event)
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             reasoning_effort="low",
#             response_format=GPTOutput,
#         )

#         result = [
#             scene.model_dump(by_alias=True)
#             for scene in response.choices[0].message.parsed.scenes
#         ]
#         result = json.dumps(result, ensure_ascii=False)

#         return result
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# async def chatgpt_doc_parser_extract(
#     req_body: ReqDoAnalysis,
#     images: list,
#     prompt: str,
#     sys_instruct: Optional[str] = None,
#     small_images: list = [],
#     db: Session = None,
# ):
#     try:
#         # AI-ANALYSIS-000002
#         client = chatgpt_client()
#         mime_type = "image/jpeg"

#         docs = [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await download_and_encode_image(mime_type, image)},
#             }
#             for image in images
#         ]
#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []

#         extra_data = []
#         if len(small_images):
#             extra_data.append({"type": "text", "text": "LIST OF SMALL IMAGES"})
#             extra_data.extend(
#                 [
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": await download_and_encode_image(
#                                 mime_type, small_image
#                             )
#                         },
#                     }
#                     for small_image in small_images
#                 ]
#             )

#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": prompt}, *docs, *extra_data],
#             }
#         ]
#         # progres 백그라운드 task 처리
#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(req_body, db, progress_event)
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             reasoning_effort="low",
#             response_format=GPTOutput,
#         )

#         result = [
#             scene.model_dump(by_alias=True)
#             for scene in response.choices[0].message.parsed.scenes
#         ]
#         result = json.dumps(result, ensure_ascii=False)

#         return result
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e
#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# async def chatgpt_image_ocr(
#     image_url: str,
#     prompt: str,
#     sys_instruct: Optional[str] = None,
# ):
#     """
#     이미지 ocr
#     """
#     try:
#         # AI-ANALYSIS-000003
#         client = chatgpt_client()
#         mime_type = "image/jpeg"

#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": await download_and_encode_image(mime_type, image_url)
#                         },
#                     },
#                 ],
#             }
#         ]

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_4_O,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             # reasoning_effort="low", # for thinking models
#             response_format=GPTOutput_OCR_Ratio,
#         )

#         result = []
#         result.append(json.loads(response.choices[0].message.content))
#         logger.info(json.dumps(result, ensure_ascii=False))

#         return result

#     except Exception as e:
#         logger.error(f"이미지 OCR 중 오류 발생: {e}", exc_info=True)
#         raise e


# async def chatgpt_image_generation(
#     req_body: ReqDoAnalysis,
#     prompt: str,
#     document_file_path: str,
#     size: Optional[str] = "1024x1536",
# ):
#     """
#     이미지 생성
#     """
#     try:
#         # AI-ANALYSIS-000003
#         client = chatgpt_client()

#         with open(document_file_path, "rb") as image:
#             response = await client.images.edit(
#                 model=LLM.GPT_IMAGE_1, image=image, prompt=prompt, n=1, size=size
#             )

#         result_image_base64 = response.data[0].b64_json
#         result_image_bytes = base64.b64decode(result_image_base64)

#         # s3 이미지 업로드
#         s3_bucket = get_s3_bucket(req_body.analysisS3)
#         s3_prefix = req_body.analysisS3.split(f"{s3_bucket}/")[1]

#         mime_type = "image/jpeg"
#         extension = get_extension(mime_type)
#         file_path = f"{S3.IMAGE_PATH}{S3.GENERATOR_IMAGE_NAME}{extension}"
#         s3_key = f"{s3_prefix}{file_path}"

#         await upload_s3_binary(s3_bucket, s3_key, result_image_bytes, mime_type)

#         return s3_key

#     except openai.OpenAIError as e:
#         raise e
#     except Exception as e:

#         logger.error(f"이미지 생성 중 오류 발생: {e}", exc_info=True)
#         raise e


# async def chatgpt_image_context(
#     req_body: ReqDoAnalysis, _prompt: list, document_files: list, db: Session
# ):
#     """
#     이미지 context 생성
#     """
#     try:
#         # ai-photo2video-000001
#         client = chatgpt_client()
#         prompt = _prompt["prompt_1"]
#         sys_instruct = _prompt["system_instruction"]

#         image_message = [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await encode_file_base64(document_file)},
#             }
#             for document_file in document_files
#         ]

#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": prompt}, *image_message],
#             }
#         ]
#         logger.info("이미지 to 컨텍스트 생성 요청")
#         # progres 백그라운드 task 처리

#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(
#                 req_body, db, progress_event, start_progress=0, end_progress=20
#             )
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_4_O,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTImage2ContextList,
#             temperature=1,
#             # reasoning_effort="low", # for thinking models
#         )

#         result = response.choices[0].message.content
#         logger.info(f"이미지 to 컨텍스트 생성: {result}")

#         return result
#     except openai.OpenAIError as e:
#         raise e
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# async def chatgpt_context_script(
#     req_body: ReqDoAnalysis, _prompt: str, gps_info: str, context: str, db: Session
# ):
#     """
#     context script 생성
#     """
#     try:
#         # ai-photo2video-000001
#         client = chatgpt_client()
#         prompt = _prompt["prompt_1"]
#         sys_instruct = _prompt["system_instruction"]
#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "text", "text": gps_info},
#                     {"type": "text", "text": context},
#                 ],
#             }
#         ]

#         logger.info("컨텍스트 to script 생성 요청")
#         # progres 백그라운드 task 처리
#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(
#                 req_body, db, progress_event, start_progress=20, end_progress=30
#             )
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_4_O,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTContext2ScriptList,
#             temperature=1.1,
#             # reasoning_effort="low", # for thinking models
#         )

#         result = response.choices[0].message.content
#         logger.info(f"컨텍스트 to 스크립트 생성: {result}")

#         return result
#     except openai.OpenAIError as e:
#         raise e
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# async def chatgpt_context_video(
#     req_body: ReqDoAnalysis,
#     _prompt: list,
#     document_files: list,
#     context: str,
#     db: Session,
# ):
#     """
#     영상 프롬프트 생성
#     """
#     try:
#         # ai-photo2video-000001
#         client = chatgpt_client()
#         prompt = _prompt["prompt_1"]
#         sys_instruct = _prompt["system_instruction"]

#         image_message = [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await encode_file_base64(document_file)},
#             }
#             for document_file in document_files
#         ]

#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "text", "text": context},
#                     *image_message,
#                 ],
#             }
#         ]
#         logger.info("컨텍스트 to 영상 프롬프트 생성 요청")
#         # progres 백그라운드 task 처리

#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(
#                 req_body, db, progress_event, start_progress=30, end_progress=50
#             )
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_4_O,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTContext2VideoList,
#             temperature=1,
#             # reasoning_effort="low", # for thinking models
#         )

#         result = response.choices[0].message.content
#         logger.info(f"이미지 to 컨텍스트 생성: {result}")

#         return result
#     except openai.OpenAIError as e:
#         raise e
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# # GPT category based request


# async def chatgpt_image_category(
#     req_body: ReqDoAnalysis, _prompt: list, document_files: list, db: Session
# ):
#     """
#     이미지 context 생성
#     """
#     try:
#         # ai-photo2video-000001
#         client = chatgpt_client()
#         prompt = _prompt["image_category"]["prompt_1"]
#         sys_instruct = _prompt["image_category"]["system_instruction"]

#         image_message = [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await encode_file_base64(document_file)},
#             }
#             for document_file in document_files
#         ]

#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": prompt}, *image_message],
#             }
#         ]
#         logger.info("이미지 to category 생성 요청")
#         # progres 백그라운드 task 처리

#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(
#                 req_body, db, progress_event, start_progress=0, end_progress=25
#             )
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTPhoto2VideoCategoryOutput,
#             temperature=1,
#             # reasoning_effort="low", # for thinking models
#         )

#         result: GPTPhoto2VideoCategoryOutput = response.choices[0].message.parsed
#         logger.info(
#             f"이미지 to category 생성: {json.dumps(result.model_dump(), ensure_ascii=False)}"
#         )

#         return result
#     except openai.OpenAIError as e:
#         raise e
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# async def chatgpt_photo_video(
#     req_body: ReqDoAnalysis,
#     _prompt: dict,
#     document_files: list,
#     locations: list,
#     db: Session,
# ):
#     """
#     이미지 to 텍스트, video 프롬프트 생성
#     """
#     RETRY_LIMIT = 5
#     retry_count = 0

#     while retry_count < RETRY_LIMIT:
#         try:
#             # ai-photo2video-000001
#             client = chatgpt_client()
#             prompt = _prompt["prompt_1"]
#             sys_instruct = _prompt["system_instruction"]

#             image_message = []

#             for document_file, location in zip(document_files, locations):
#                 image_message.append(
#                     {
#                         "type": "image_url",
#                         "image_url": {"url": await encode_file_base64(document_file)},
#                     }
#                 )
#                 if not location:
#                     location = "No Location"
#                 image_message.append({"type": "text", "text": location})

#             messages = (
#                 [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#             )
#             messages = messages + [
#                 {
#                     "role": "user",
#                     "content": [{"type": "text", "text": prompt}, *image_message],
#                 }
#             ]
#             logger.info("이미지 to 텍스트, video 프롬프트 생성 요청")
#             # progres 백그라운드 task 처리

#             progress_event = asyncio.Event()
#             progress_task = asyncio.create_task(
#                 update_progress_background(
#                     req_body, db, progress_event, start_progress=0, end_progress=20
#                 )
#             )

#             response = await client.beta.chat.completions.parse(
#                 model=LLM.GPT_O_4_MINI,
#                 messages=messages,
#                 max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#                 response_format=GPTPhoto2VideoOutputs,
#                 temperature=1,
#                 # reasoning_effort="low", # for thinking models
#             )

#             result: GPTPhoto2VideoOutputs = response.choices[0].message.parsed
#             if result == None:
#                 raise Exception(
#                     ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_POLICY_VIOLATION_IMAGE
#                 )
#             else:
#                 result = result.model_dump()  # to dict

#             logger.info(
#                 f"이미지 to 텍스트, video 프롬프트 생성: {json.dumps(result, ensure_ascii=False)}"
#             )

#             # fix: infinite process when LLM result != document_files
#             if len(result["results"]) != len(document_files):
#                 raise AssertionError(
#                     (
#                         "LLM result size should equal to document_files size :"
#                         f"{len(result['results'])} != {len(document_files)} "
#                     )
#                 )

#             return result

#         except AssertionError as ae:
#             retry_count += 1
#             logger.warning(f"실패: {ae} - 재시도 {retry_count}회")

#             if retry_count >= RETRY_LIMIT:
#                 logger.error(f"재시도{retry_count}회 실패. 분석 중 오류")
#                 raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_RETRY_LIMIT_EXCEEDED)
#             await asyncio.sleep(5)

#         except Exception as e:
#             logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#             raise e

#         finally:
#             # 백그라운드 progress task 종료
#             if progress_event:
#                 progress_event.set()
#             if progress_task:
#                 await progress_task


# async def chatgpt_photo_music(
#     req_body: ReqDoAnalysis, document_files: list, db: Session
# ):
#     """
#     이미지 to 음악 프롬프트 생성
#     """
#     try:
#         client = chatgpt_client()
#         prompt = """
# Based on the following input, generate a single line of BGM tags only, separated by commas.
# """
#         sys_instruct = """
# You are a helpful AI assistant specialized in analyzing multiple images and expressing their combined mood.
# You will be given between 1 and 4 images, each depicting any subject (people, objects, scenes, products, etc.).

# Your task is to analyze the input images and suggest one mood that fits all of them.
# Provide comma-separated list of tags that fits the mood.
# The tags should be at least 3, maximum 10 tags.

# For example:
# ex1) "calm, midtempo, soft piano, warm pad, low energy, major key, acoustic, background study"
# ex2) "hopeful, slow tempo, ambient synth, gentle rhythm, expansive, major key, travel vlog"
# ex3) "suspenseful, slow build, string swell, rising tension, sparse arrangement, minor key, cinematic underscore"

# Output Format:
# "tag1, tag2, tag3, ..."
# """

#         image_message = [
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await encode_file_base64(document_file)},
#             }
#             for document_file in document_files
#         ]

#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [{"type": "text", "text": prompt}, *image_message],
#             }
#         ]

#         # progress_event = asyncio.Event()
#         # progress_task = asyncio.create_task(
#         #     update_progress_background(
#         #         req_body, db, progress_event, start_progress=0, end_progress=20
#         #     )
#         # )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTPhoto2MusicOutput,
#             temperature=1,
#             # reasoning_effort="low", # for thinking models
#         )

#         result: GPTPhoto2MusicOutput = response.choices[0].message.parsed

#         logger.info(
#             f"이미지 to 음악 프롬프트 생성: {json.dumps(result.model_dump(), ensure_ascii=False)}"
#         )

#         return result
#     except openai.OpenAIError as e:
#         raise e
#     except Exception as e:
#         logger.error(f"이미지 to 음악 프롬프트 생성 중 오류 발생: {e}", exc_info=True)
#         raise e
#     # finally:
#     #     # 백그라운드 progress task 종료
#     #     if progress_event:
#     #         progress_event.set()
#     #     if progress_task:
#     #         await progress_task


# async def chatgpt_enhance_prompt(
#     req_body: ReqDoAnalysis,
#     _prompt: dict,
#     document_file: str,
#     db: Session,
# ):
#     """
#     이미지 to 텍스트, video 프롬프트 생성
#     """

#     # 변수 초기화를 while 루프 밖으로 이동
#     progress_event = None
#     progress_task = None

#     try:
#         # ai-photo2video-000001
#         client = chatgpt_client()
#         user_input = req_body.option[0].value
#         prompt = _prompt["prompt_1"]
#         sys_instruct = _prompt["system_instruction"]

#         image_message = []
#         image_message.append(
#             {
#                 "type": "image_url",
#                 "image_url": {"url": await encode_file_base64(document_file)},
#             }
#         )

#         messages = [{"role": "system", "content": sys_instruct}] if sys_instruct else []
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "text", "text": user_input},
#                     *image_message,
#                 ],
#             }
#         ]

#         logger.info("enhanced video 프롬프트 생성 요청")

#         # progress 백그라운드 task 처리
#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(
#                 req_body, db, progress_event, start_progress=0, end_progress=20
#             )
#         )

#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTContext2Video,
#             temperature=1,
#             # reasoning_effort="low", # for thinking models
#         )

#         result: GPTContext2Video = response.choices[0].message.parsed
#         if result == None:
#             raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_POLICY_VIOLATION_PROMPT)
#         else:
#             result = result.model_dump()

#         logger.info(f"enhanced prompt: {json.dumps(result, ensure_ascii=False)}")

#         return result  # 성공 시 바로 반환

#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task


# async def chatgpt_analysis_assist(
#     req_body: ReqLLMAssist, prompt: str, db: Session
# ) -> str:
#     """
#     req_bot, 어시스트 프롬프트로 GPT API 요청

#     Args:
#         req_body (ReqLLMAssist) 어시스트 req_body
#         db (Session): db 세션

#     Returns:
#         str: GPT API에서 생성된 텍스트 출력.
#     """
#     try:
#         client = chatgpt_client()
#         input_data = req_body.inputData

#         progress_event = asyncio.Event()
#         progress_task = asyncio.create_task(
#             update_progress_background(
#                 req_body, db, progress_event, start_progress=0, end_progress=20
#             )
#         )

#         # messages = [{"role": "system", "content": system_instruction}] if system_instruction else []
#         messages = [{"role": "system", "content": "You are a helpful assistant."}]
#         messages = messages + [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "text", "text": input_data},
#                 ],
#             }
#         ]
#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_O_4_MINI,
#             messages=messages,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             temperature=1,
#             reasoning_effort="low",  # for thinking models
#         )

#         progress = 0
#         result = response.choices[0].message.content

#         return result
#     except openai.OpenAIError as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e
#     except Exception as e:
#         logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
#         raise e

#     finally:
#         # 백그라운드 progress task 종료
#         if progress_event:
#             progress_event.set()
#         if progress_task:
#             await progress_task



# async def chatgpt_image_keywords(document: str) -> Optional[str]:
#     """
#     OpenAI GPT-4O를 사용하여 이미지에서 키워드 추출

#     Args:
#         image_path: 분석할 이미지 파일 경로

#     Returns:
#         추출된 키워드 문자열 또는 None (실패시)
#     """
#     try:
#         # OpenAI 클라이언트 생성
#         client = chatgpt_client()

#         # 이미지를 base64로 인코딩
#         base64_image = await encode_file_base64(document)

#         prompt = """You are an expert image analyst specializing in location identification. Analyze this image and extract 2-3 highly specific Korean keywords that would be most effective for Google search to identify the exact location or place.

# Instructions:
# 1. Prioritize unique, distinctive features that would differentiate this location from similar places
# 2. Focus on landmarks, architectural elements, signage, or notable geographical features
# 3. If no distinctive features are visible, identify the most specific objects, landscape elements, or scene types
# 4. Choose keywords that are searchable and commonly used in Korean

# Output format:
# - Provide exactly 2-3 keywords in Korean
# - List them in order of search effectiveness (most distinctive first)
# - Each keyword should be 1-4 words maximum
# """
#         # OpenAI API 호출
#         response = await client.beta.chat.completions.parse(
#             model=LLM.GPT_4_O,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": prompt,
#                         },
#                         {
#                             "type": "image_url",
#                             "image_url": {"url": base64_image},
#                         },
#                     ],
#                 }
#             ],
#             # top_p=1,
#             max_completion_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
#             response_format=GPTGps2KeywordList,
#         )

#         keywords = json.loads(response.choices[0].message.content.strip())
#         result = keywords["keywords"]

#         return result

#     except Exception as e:
#         logger.warning(f"키워드 추출 중 오류 발생: {e}")
#         return []