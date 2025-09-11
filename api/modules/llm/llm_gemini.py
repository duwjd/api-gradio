import asyncio
import base64
import logging
import json
from base64 import b64encode
from io import BytesIO
from typing import Optional

from google import genai
from google.genai import types
from PIL.ImageFile import ImageFile
from sqlalchemy.orm import Session

from api.modules.analysis.dao.analysis_task_llm_dao import update_task_llm_progress
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from api.modules.llm.llm_util import update_progress_background
from api.modules.llm.schema.llm_schema import ReqDoLLM, ReqLLMAssist
from api.modules.llm.schema.llm_gemini_schema import (
    GeminiPhoto2VideoOutputs,
    GeminiContext2Video,
    GeminiGps2KeywordList
    )
from config.const import ANALYSIS_ERROR
from config.llm_const import LLM, GEMINIParams, LLMConfig
from utils.google_util import gemini_client_async, genai_client
from utils.http_util import load_file_url
from utils.util import get_mime_type, encode_file_base64

import mimetypes

logger = logging.getLogger("app")


def temp_base64(image: ImageFile, size=(1920, 1024)):
    """
    이미지 base64
    """
    buffer = BytesIO()

    image.resize(size).convert("RGB").save(buffer, "JPEG")
    buffer.seek(0)
    bytes = b64encode(buffer.getbuffer())
    buffer.close()
    return bytes.decode("utf-8")


async def gemini_analysis_assist(
    req_body: ReqLLMAssist, prompt: str, db: Session
) -> str:
    """
    req_bot, 어시스트 프롬프트로 Gemini API 요청

    Args:
        req_body (ReqLLMAssist) 어시스트 req_body
        db (Session): db 세션

    Returns:
        str: Gemini API에서 생성된 텍스트 출력.
    """
    input_data = req_body.inputData

    contents = [
        prompt,
        genai.types.Part.from_text(text=input_data),
    ]

    config = {
        "max_output_tokens": LLMConfig.MAX_OUTPUT_TOKENS,
        "temperature": GEMINIParams.TEMPERATURE,
        "top_p": GEMINIParams.TOP_P,
    }

    response = genai_client().models.generate_content_stream(
        model=LLM.GEMINI_2_5_PRO,
        config=config,
        contents=contents,
    )

    result = ""
    progress = 0

    for chunk in response:
        result += chunk.text

        if progress <= 95:
            progress += 10
            await update_task_llm_progress(req_body, progress, db)

    return result


async def gemini_analysis_engine(req_body: ReqDoLLM, db: Session) -> str:
    """
    텍스트, 파일을 입력으로 받아 Gemini API를 통해 텍스트 분석 및 요약을 수행하는 함수.

    Args:
        req_body (ReqDoLLM) 분석 req_body
        db (Session): db 세션

    Returns:
        str: Gemini API에서 생성된 텍스트 출력.
    """
    input_data = req_body.inputData
    prompt = req_body.prompt
    system_prompt = req_body.systemPrompt

    genai_client = await gemini_client_async()
    type = req_body.type
    if type == "text":
        contents = [
            prompt,
            genai.types.Part.from_text(text=input_data),
        ]
    elif type == "file":
        file_data = await load_file_url(input_data)
        mime_type = get_mime_type(input_data)

        contents = [
            prompt,
            genai.types.Part.from_bytes(data=file_data, mime_type=mime_type),
        ]

    elif type == "multi":

        file_parts = []

        for url in input_data:
            file_data = await load_file_url(url)
            mime_type = get_mime_type(url)
            file_parts.append(
                genai.types.Part.from_bytes(data=file_data, mime_type=mime_type)
            )

        contents = [prompt, *file_parts]

    config = {
        "max_output_tokens": LLMConfig.MAX_OUTPUT_TOKENS,
        "temperature": GEMINIParams.TEMPERATURE,
        "top_p": GEMINIParams.TOP_P,
        "response_mime_type": "application/json",
    }

    if system_prompt:
        config["system_instruction"] = system_prompt

    response = genai_client.models.generate_content_stream(
        model=LLM.GEMINI_2_5_PRO,
        config=config,
        contents=contents,
    )

    result = ""
    # progress = req_body.startProgress

    # for chunk in response:
    #     result += chunk.text

    #     if progress < req_body.endProgress and progress <= 95:
    #         progress += 5
    #         await update_task_llm_progress(req_body, progress, db)
    #         logger.info(f"progress : {progress}")

    logger.info(f"요청 결과 : {result}")

    return result


async def gemini_doc_parser_image(
    req_body: ReqDoAnalysis,
    images: list,
    prompt: str,
    sys_instruct: Optional[str] = None,
    small_images: list = [],
    db: Session = None,
):
    """
    PDF 파일을 입력으로 받아 Gemini API를 통해 텍스트 분석 및 요약을 수행하는 함수.

    Args:
        request (Request): fast api Request
        document_path (str): 분석할 파일의 경로.
        sys_instruct (str): 시스템 지시문(System Instruction)으로, 모델의 동작 방식에 영향을 줌.
        prompt (str): 모델에 전달할 추가 프롬프트(질문 또는 요청).
        mime_type (str): 모델에 전달할 MIME 타입

    Returns:
        str: Gemini API에서 생성된 텍스트 출력.
    """
    try:
        logger.info("[LLM-GEMINI] doc parser image llm 요청")
        genai_client = await gemini_client_async()
        docs = [
            genai.types.Part.from_bytes(
                data=await load_file_url(image), mime_type="image/jpeg"
            )
            for image in images
        ]
        extra_data = []

        if len(small_images):
            extra_data.append("LIST OF IMAGES")
            extra_data.extend(
                [
                    genai.types.Part.from_bytes(
                        data=await load_file_url(image), mime_type="image/jpeg"
                    )
                    for image in small_images
                ]
            )

        contents = [prompt] + docs + extra_data

        config = types.GenerateContentConfig(
            max_output_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
            temperature=GEMINIParams.TEMPERATURE,
            top_p=GEMINIParams.TOP_P,
            response_mime_type="application/json",
            # thinking_config=types.ThinkingConfig(
            #     include_thoughts=False, thinking_budget=3000
            # ),
        )
        if sys_instruct is not None:
            config.system_instruction = sys_instruct

        # progres 백그라운드 task 처리
        progress_event = asyncio.Event()
        progress_task = asyncio.create_task(
            update_progress_background(req_body, db, progress_event)
        )
        response = await asyncio.to_thread(
            genai_client.models.generate_content,
            model=LLM.GEMINI_2_5_PRO,
            config=config,
            contents=contents,
        )
        # 생성된 텍스트를 반환
        result = response.text

        return result
    except Exception as e:
        logger.error(e)
        raise e

    finally:
        # 백그라운드 progress task 종료
        if progress_event:
            progress_event.set()
        if progress_task:
            await progress_task


async def gemini_doc_parser_extract(
    req_body: ReqDoAnalysis,
    images: list,
    prompt: str,
    sys_instruct: Optional[str] = None,
    small_images: list = [],
    db: Session = None,
):
    """
    PDF 파일을 입력으로 받아 Gemini API를 통해 텍스트 분석 및 요약을 수행하는 함수.

    Args:
        request (Request): fast api Request
        document_path (str): 분석할 파일의 경로.
        sys_instruct (str): 시스템 지시문(System Instruction)으로, 모델의 동작 방식에 영향을 줌.
        prompt (str): 모델에 전달할 추가 프롬프트(질문 또는 요청).
        mime_type (str): 모델에 전달할 MIME 타입

    Returns:
        str: Gemini API에서 생성된 텍스트 출력.
    """
    try:
        genai_client = await gemini_client_async()
        docs = [
            genai.types.Part.from_bytes(
                data=await load_file_url(image), mime_type="image/jpeg"
            )
            for image in images
        ]
        extra_data = []

        if len(small_images):
            extra_data.append("LIST OF IMAGES")
            extra_data.extend(
                [
                    genai.types.Part.from_bytes(
                        data=await load_file_url(image), mime_type="image/jpeg"
                    )
                    for image in small_images
                ]
            )

        contents = [prompt] + docs + extra_data

        config = types.GenerateContentConfig(
            max_output_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
            temperature=GEMINIParams.TEMPERATURE,
            top_p=GEMINIParams.TOP_P,
            response_mime_type="application/json",
            # thinking_config=types.ThinkingConfig(
            #     include_thoughts=False, thinking_budget=3000
            # ),
        )
        if sys_instruct is not None:
            config.system_instruction = sys_instruct

        # progres 백그라운드 task 처리
        progress_event = asyncio.Event()
        progress_task = asyncio.create_task(
            update_progress_background(req_body, db, progress_event)
        )
        response = await asyncio.to_thread(
            genai_client.models.generate_content,
            model=LLM.GEMINI_2_5_PRO,
            config=config,
            contents=contents,
        )
        # 생성된 텍스트를 반환
        result = response.text

        return result
    except Exception as e:
        logger.error(e)
        raise e

    finally:
        # 백그라운드 progress task 종료
        if progress_event:
            progress_event.set()
        if progress_task:
            await progress_task

async def gemini_photo_video(
    req_body: ReqDoAnalysis,
    _prompt: dict,
    document_files: list,
    locations: list,
    db: Session,
):
    """
    이미지 to 텍스트, video 프롬프트 생성
    """
    RETRY_LIMIT = 5
    retry_count = 0
    
    while retry_count < RETRY_LIMIT:
        try:
            # ai-photo2video-000001
            genai_client = await gemini_client_async()
            system_instruction = _prompt["system_instruction"]
            prompt = _prompt["prompt_1"]
            
            image_contents = []
            
            for document_file, location in zip(document_files, locations):
                data_url = await encode_file_base64(document_file)
                # logger.info("data_url(head30): %s%s", data_url[:50], "..." if len(data_url) > 50 else "")
                b64 = data_url.split(",", 1)[1]
                raw = base64.b64decode(b64)
                # logger.info("raw(head30): %s%s", raw[:50], b"..." if len(raw) > 50 else b"")
                
                image_contents.append(
                    types.Part.from_bytes(
                        data= raw, 
                        mime_type="image/jpeg"
                    )
                )
                if not location:
                    location = "No Location"
                image_contents.append(types.Part.from_text(text=location))
                
            system_instruction = system_instruction if system_instruction else ""
            contents = [
                types.Part.from_text(text=prompt), *image_contents,
            ]
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
                temperature=1,
                response_mime_type="application/json",
                response_schema=GeminiPhoto2VideoOutputs.SCHEMA,
                # thinking_config=types.ThinkingConfig(
                #     include_thoughts=False, thinking_budget=3000
                # ),
            )
            logger.info(("이미지 to 텍스트, video 프롬프트 생성"))
            
            progress_event = asyncio.Event()
            progress_task = asyncio.create_task(
                update_progress_background(
                    req_body, db, progress_event, start_progress=0, end_progress=20
                )
            )
            
            response = await asyncio.to_thread(
                genai_client.models.generate_content,
                model=LLM.GEMINI_2_5_PRO,
                config=config,
                contents=contents,
            )
            # 생성된 텍스트를 반환
            result = response.parsed # 딕셔너리
            if result == None:
                raise Exception(
                    ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_POLICY_VIOLATION_IMAGE
                )
            
            logger.info(
                f"이미지 to 텍스트, video 프롬프트 생성: {json.dumps(result, ensure_ascii=False)}"
            )
            
            if len(result["results"]) != len(document_files):
                raise AssertionError(
                    (
                        "LLM result size should equal to document_files size :"
                        f"{len(result['results'])} != {len(document_files)} "
                    )
                )
            
            return result

        except AssertionError as ae:
            retry_count += 1
            logger.warning(f"실패: {ae} - 재시도 {retry_count}회")
            
            if retry_count>= RETRY_LIMIT:
                logger.error(f"재시도{retry_count}회 실패. 분석 중 오류")
                raise Exception(
                    ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_RETRY_LIMIT_EXCEEDED
                )
            await asyncio.sleep(5)
        
        except Exception as e:
            logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
            raise e

        finally:
            # 백그라운드 progress task 종료
            if progress_event:
                progress_event.set()
            if progress_task:
                await progress_task


async def gemini_enhance_prompt(
    req_body: ReqDoAnalysis,
    _prompt: dict,
    document_file: str,
    db: Session,
):
    """
    이미지 to 텍스트, video 프롬프트 생성
    """
    
    # 변수 초기화를 while 루프 밖으로 이동
    progress_event = None
    progress_task = None
    
    try:
        # ai-photo2video-000001
        genai_client = await gemini_client_async()
        user_input = req_body.option[0].value
        system_instruction = _prompt["system_instruction"]
        prompt = _prompt["prompt_1"]
        
        image_contents = []
        
        data_url = await encode_file_base64(document_file)
        # logger.info("data_url(head30): %s%s", data_url[:50], "..." if len(data_url) > 50 else "")
        b64 = data_url.split(",", 1)[1]
        raw = base64.b64decode(b64)
        # logger.info("raw(head30): %s%s", raw[:50], b"..." if len(raw) > 50 else b"")
        image_contents.append(
            types.Part.from_bytes(
                data= raw,
                mime_type="image/jpeg"
            )
        )
        
        contents = [
            types.Part.from_text(text=prompt), 
            types.Part.from_text(text=user_input),
            *image_contents,
        ]
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
            temperature=1,
            response_mime_type="application/json",
            response_schema=GeminiContext2Video.SCHEMA,
            # thinking_config=types.ThinkingConfig(
            #     include_thoughts=False, thinking_budget=3000
            # ),
        )
        logger.info(f"enhanced video 프롬프트 생성 요청")
        
        # progress 백그라운드 task 처리
        progress_event = asyncio.Event()
        progress_task = asyncio.create_task(
            update_progress_background(
                req_body, db, progress_event, start_progress=0, end_progress=20
            )
        )
        
        response = await asyncio.to_thread(
            genai_client.models.generate_content,
            model=LLM.GEMINI_2_5_PRO,
            config=config,
            contents=contents,
        )
        # 생성된 텍스트를 반환
        result = response.parsed # 딕셔너리
        if result == None:
            raise Exception(
                ANALYSIS_ERROR.AI_API_ANALYSIS_LLM_POLICY_VIOLATION_IMAGE
            )
        
        logger.info(
            f"enhanced prompt: {json.dumps(result, ensure_ascii=False)}"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}", exc_info=True)
        raise e

    finally:
        # 백그라운드 progress task 종료
        if progress_event:  
            progress_event.set()
        if progress_task:
            await progress_task 


async def gemini_image_keywords(document_file: str) -> Optional[str]:
    """
    Gemini를 사용하여 이미지에서 키워드 추출

    Args:
        image_path: 분석할 이미지 파일 경로

    Returns:
        추출된 키워드 문자열 또는 None (실패시)
    """
    try:
        genai_client = await gemini_client_async()
        system_instruction = """
        """
        prompt = """
You are an expert image analyst specializing in location identification. Analyze this image and extract 2-3 highly specific Korean keywords that would be most effective for Google search to identify the exact location or place.

Instructions:
1. Prioritize unique, distinctive features that would differentiate this location from similar places
2. Focus on landmarks, architectural elements, signage, or notable geographical features
3. If no distinctive features are visible, identify the most specific objects, landscape elements, or scene types
4. Choose keywords that are searchable and commonly used in Korean

Output format:
- Provide exactly 2-3 keywords in Korean
- List them in order of search effectiveness (most distinctive first)
- Each keyword should be 1-4 words maximum        
"""
        
        mime_type, _ = mimetypes.guess_type(document_file)
        data_url = await encode_file_base64(document_file)
        b64 = data_url.split(",", 1)[1]
        raw = base64.b64decode(b64)
        
        # # ToDo: 확장자가 없거나 특이하면 None 이 나올 가능성이 있다고함
        # if mime_type is None:
        #     raise e
        
        system_instruction = system_instruction if system_instruction else ""
        contents = [
            types.Part.from_text(text=prompt), 
            types.Part.from_bytes(data=raw, mime_type=mime_type),
        ]
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=LLMConfig.MAX_OUTPUT_TOKENS,
            temperature=1,
            response_mime_type="application/json",
            response_schema=GeminiGps2KeywordList.SCHEMA,
            # thinking_config=types.ThinkingConfig(
            #     include_thoughts=False, thinking_budget=3000
            # ),            
        )
        
        response = await asyncio.to_thread(
            genai_client.models.generate_content,
            model=LLM.GEMINI_2_5_PRO,
            config=config,
            contents=contents,
        )
        
        result = response.parsed
        keywords = json.loads(json.dumps({"keywords": result.get('keywords')}, ensure_ascii=False))
        return keywords
    
    except Exception as e:
        logger.warning(f"키워드 추출 중 오류 발생: {e}")
        return []