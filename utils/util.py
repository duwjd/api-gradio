import asyncio
import base64
import importlib
import importlib.util
import logging
import mimetypes
import os
import posixpath
import re
from io import BytesIO
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import aiohttp
import fitz
import pymupdf
from PIL import ExifTags, Image, ImageOps, PngImagePlugin

from config.const import ANALYSIS_ERROR, DOCUMENT_TYPE, PROMPT_TYPE, MimeType

# 로커 설정
logger = logging.getLogger("app")

# 현재 util.py가 있는 디렉토리 기준으로 prompts 폴더 경로 설정
BASE_PROMPT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "prompts"
)

# PIL 이미지 픽셀 제한 해제
Image.MAX_IMAGE_PIXELS = None


def build_status_key(env: str, user_id: str, project_id: str) -> str:
    """
    Redis 등에 사용될 status_key 문자열을 생성

    Args:
        user_id (str): 사용자 ID
        project_id (str): 프로젝트 ID

    Returns:
        str: f"{APP_ENVIRONMENT}:cat-ai:document:{user_id}:{project_id}" 형식의 문자열
    """
    return f"{env}:cat-ai:document:{user_id}:{project_id}"


def get_prompt(
    group: Optional[str] = None,
    doc_type: Optional[str] = None,
    prompt_type: Optional[str] = None,
    llm_code: Optional[str] = None,
):
    """
    특정 group, doc_type 조합에 해당하는 프롬프트 파일을 독립적으로 로드

    Args:
        group (str): 도메인 그룹 (예: 'samsung')
        doc_type (str): 문서 타입 (예: 'document', 'pamphlet' 등)

    Returns:
        dict: _prompt 딕셔너리 (모듈에 정의되어 있는 경우)
        또는 None (pamphlet 등 프롬프트가 필요 없는 경우)

    Raises:
        FileNotFoundError: 프롬프트 파일이 없을 때
        AttributeError: _prompt 변수가 정의되지 않았을 때
        Exception: 기타 알 수 없는 오류
    """
    if prompt_type == PROMPT_TYPE.OCR:
        prompt_file_path = os.path.join(BASE_PROMPT_DIR, f"{prompt_type.lower()}.py")
        if not os.path.exists(prompt_file_path):
            raise FileNotFoundError(
                f"해당 프롬프트 파일이 존재하지 않습니다: {prompt_file_path}"
            )
    else:
        if not group or not doc_type:
            raise ValueError("group 또는 doc_type이 필요합니다.")
        # `group`에서 ".com" 제거 및 소문자로 변환

        if not llm_code:
            raise ValueError("llm_code가 필요합니다 (ex: LLM-GEMINI, LLM-CHATGPT).")
        # `group`에서 ".com" 제거 및 소문자로 변환

        remove_suffixes = [".co.kr", ".com", ".demo"]
        for suffix in remove_suffixes:
            if group.endswith(suffix):
                group = group[: -len(suffix)]
                break  # 매칭된 첫 번째 도메인만 제거

        sanitized_group = group.lower()
        doc_type = doc_type.lower()

        # 해당 프롬프트 파일 경로 정의
        prompt_file_path = os.path.join(
            BASE_PROMPT_DIR, llm_code, sanitized_group, f"{doc_type}.py"
        )
        # 파일이 존재하는지 확인
        if not os.path.exists(prompt_file_path):
            if doc_type == DOCUMENT_TYPE.PAMPHLET:
                return None
            elif doc_type == DOCUMENT_TYPE.GG_PROJECT:
                logger.warning(
                    f"{sanitized_group} 그룹에 gg-project에 대한 프롬프트가 없어 gemgem 그룹에 있는 프롬프트 파일을 사용합니다."
                )
                prompt_file_path = os.path.join(
                    BASE_PROMPT_DIR, "gemgem", f"{doc_type}.py"
                )
            elif doc_type == DOCUMENT_TYPE.GG_PROJECT:
                logger.warning(
                    f"{sanitized_group} 그룹에 gg-project에 대한 프롬프트가 없어 gemgem 그룹에 있는 프롬프트 파일을 사용합니다."
                )
                prompt_file_path = os.path.join(
                    BASE_PROMPT_DIR, "gemgem", f"{doc_type}.py"
                )
            else:
                raise FileNotFoundError(
                    f"해당 프롬프트 파일이 존재하지 않습니다: {prompt_file_path}"
                )
    try:
        # 동적으로 Python 모듈 로드
        spec = importlib.util.spec_from_file_location("prompt_module", prompt_file_path)
        prompt_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prompt_module)
        logger.info(f"프롬프트 로드 성공: {prompt_file_path}")
        # `_prompt` 변수를 가져오기
        if hasattr(prompt_module, "_prompt"):
            prompt_data = prompt_module._prompt
            return prompt_data
        else:
            raise AttributeError(
                f"{prompt_file_path} 모듈에 '_prompt' 변수가 정의되지 않았습니다."
            )
    except Exception as e:
        raise Exception(f"프롬프트 로딩 중 오류 발생: {str(e)}")


def get_mime_type(file_path: str) -> str:
    """
    파일의 MIME 타입 구하기

    Args:
        file_path (str): 확인할 파일의 경로

    Returns:
        str: 파일의 MIME 타입 (예: 'image/png', 'text/plain', 'application/octet-stream')
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "application/octet-stream"  # 기본값 설정


def stream_and_tee(stream, targets, buffer=None):
    """gunicorn 로그 출력 핸들링"""
    for line in iter(stream.readline, b""):
        decoded = line.decode(errors="replace")
        for target in targets:
            try:
                target.write(decoded)
                target.flush()
            except Exception:
                pass
        if buffer is not None:
            buffer.append(decoded)
    stream.close()


async def download_and_encode_image(mime_type: str, url: str):
    """
    이미지 url 다운로드 -> base64 encoding
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download image: {response.status}")
            if mime_type.startswith("image/"):

                # 이미지 로딩
                image_bytes = await response.read()
                mime_type = response.headers.get("Content-Type", "image/jpeg")
                encoded = base64.b64encode(image_bytes).decode("utf-8")

                return f"data:{mime_type};base64,{encoded}"
            elif mime_type == "application/pdf":

                # PDF 로딩
                pdf_bytes = await response.read()
                pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
                base64_images = []

                for page in pdf_document:
                    # 렌더링 해상도 조절 (기본은 1.0, 필요시 zoom=2.0 추천)
                    pix = page.get_pixmap(dpi=200)
                    img_bytes = pix.tobytes("png")
                    encoded = base64.b64encode(img_bytes).decode("utf-8")
                    base64_images.append(f"data:image/png;base64,{encoded}")

                pdf_document.close()

                return base64_images
            else:
                raise Exception(f"Unsupported MIME type: {mime_type}")

        raise Exception(f"Unsupported file extension: {ext}")


async def open_image(file_path: str) -> Image.Image:
    """
    비동기적으로 이미지를 열어 Image.Image 객체를 반환

    Args:
        file_path (str): 열릴 이미지 파일의 경로

    Returns:
        Image.Image: 열린 이미지
    """

    def _open_image(file_path: str) -> Image.Image:
        return Image.open(file_path)

    image = await asyncio.to_thread(_open_image, file_path)
    return image

async def encode_image_base64(image: Image.Image):
    """
    이미지을 base64 encoding
    """

    def encode(image: Image.Image):
        buffer = BytesIO()
        image_format = (image.format or "JPEG").lower()
        if image.mode == "RGBA":
            image_format = "PNG"
        image.save(buffer, format=image_format.upper())
        encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
        extension = "jpeg" if image_format == "jpg" else image_format
        buffer.close()
        return f"data:image/{extension};base64,{encoded_image}"

    encoded_image = await asyncio.to_thread(encode, image)
    return encoded_image


async def encode_file_base64(file_path: str):
    """
    파일을 base64 encoding
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    async def encode_image():
        def read_image():
            with Image.open(file_path) as img:
                buffer = BytesIO()
                img.save(buffer, format=img.format)
                return buffer.getvalue(), img.format.lower()

        image_bytes, img_format = await asyncio.to_thread(read_image)
        mime_type = f"image/{'jpeg' if img_format == 'jpg' else img_format}"
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    async def encode_pdf():
        def read_pdf():
            with open(file_path, "rb") as f:
                pdf_document = fitz.open(stream=f.read(), filetype="pdf")
                images = []
                for page in pdf_document:
                    pix = page.get_pixmap(dpi=200)
                    img_bytes = pix.tobytes("png")
                    images.append(img_bytes)
                pdf_document.close()
                return images

        image_bytes_list = await asyncio.to_thread(read_pdf)
        return [
            f"data:image/png;base64,{base64.b64encode(img).decode('utf-8')}"
            for img in image_bytes_list
        ]

    if ext in [".jpg", ".jpeg", ".png"]:
        return await encode_image()
    elif ext == ".pdf":
        return await encode_pdf()
    else:
        raise Exception(f"Unsupported file extension: {ext}")


def get_extension(mime_type: str) -> str:
    """
    파일의 확장자 구하기
    """
    return mimetypes.guess_extension(mime_type)


async def remove_image_metadata(file_path: str):
    """
    EXIF Orientation을 반영한 뒤(있다면) 메타데이터를 제거하여 원본 포맷에 맞게 다시 저장.
    - PNG: 알파/팔레트 유지, 메타 제거(PngInfo 비움)
    - JPEG: EXIF/메타 제거(= exif 미전달), 필요 시 배경 합성
    - 팔레트(P) PNG는 RGBA/RGB로 변환해 '검은 화면' 문제 방지
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    def work():
        with Image.open(file_path) as img:
            # 1) EXIF Orientation 자동 반영 (JPEG/TIFF에만 의미 있음)
            fmt = (img.format or "PNG").upper()  # 'PNG', 'JPEG' 등
            try:
                img = ImageOps.exif_transpose(img)
            except Exception as e:
                logger.warning(f"EXIF transpose failed: {e}")

            # 2) 팔레트/알파 안전 처리
            #   - 'P'는 팔레트 초기화로 검게 되는 문제를 피하기 위해 변환
            if img.mode == "P":
                if "transparency" in img.info:
                    img = img.convert("RGBA")  # 투명 팔레트 → RGBA
                else:
                    img = img.convert("RGB")  # 불투명 팔레트 → RGB

            # 3) 저장(메타 제거)
            if fmt == "PNG":
                # 빈 PNG info로 저장하면 텍스트/EXIF 등 부가 메타가 사라짐.
                # (알파/팔레트/ICC 같은 필수적 시각정보는 포맷이 관리)
                pnginfo = PngImagePlugin.PngInfo()
                img.save(file_path, "PNG", optimize=True, pnginfo=pnginfo)

            elif fmt in ("JPEG", "JPG", "MPO"):
                # JPEG는 알파가 없으므로, RGBA라면 배경에 합성 후 저장해야 시각정보 보존
                if "A" in img.getbands():
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img.convert("RGBA"), mask=img.getchannel("A"))
                    img = bg
                else:
                    img = img.convert("RGB")
                # exif를 전달하지 않으면 EXIF/메타 제거됨
                img.save(file_path, "JPEG", quality=95, optimize=True)

            else:
                # 그 외 포맷은 PNG로 안전 저장(메타 제거), 알파 있으면 RGBA 유지
                pnginfo = PngImagePlugin.PngInfo()
                img.save(file_path, "PNG", optimize=True, pnginfo=pnginfo)

    await asyncio.to_thread(work)


async def is_change_image(file_path: str, extension: str):
    """
    실제 이미지 유형변환 여부 리턴

    Args:
        file_path (str): 파일 경로
        extension (str): 확장자

    Returns:
        bool: 실제 이미지 유형변환 여부
    """

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        def work():
            with Image.open(file_path) as img:
                base, _ = os.path.splitext(file_path)
                exif = img.info.get("exif")  # EXIF 원본 추출
                fmt = img.format.upper()  # 'PNG', 'JPEG' 등

                logger.info(
                    f"format: {fmt}, extension: {extension}, img_mode: {img.mode}"
                )
                if fmt != None:  # PNG, JPEG, JPG, WEBP
                    match fmt:
                        case "PNG":
                            new_ext = ".jpeg"
                        case "JPEG":
                            new_ext = ".jpeg"
                        case "JPG":
                            new_ext = ".jpg"
                        case "WEBP":
                            new_ext = ".jpeg"
                        case "MPO":
                            new_ext = ".jpeg"
                        case _:
                            raise Exception(ANALYSIS_ERROR.AI_API_INVALID_MIME_TYPE)

                    save_kwargs = {"format": fmt, "optimize": True}
                    new_file = base + new_ext
                    img = img.convert("RGB")

                    if MimeType[fmt] == MimeType.WEBP or extension == MimeType.WEBP:
                        save_kwargs["format"] = "JPEG"
                        img.save(new_file, **save_kwargs)

                        return new_file, True
                    if MimeType[fmt] != extension:
                        if exif != None:
                            save_kwargs["exif"] = exif

                        save_kwargs["format"] = "JPEG"

                        img.save(new_file, **save_kwargs)

                        return new_file, True
                else:
                    # img.format None 일 경우
                    save_kwargs = {"format": "JPEG", "optimize": True}

                    if exif != None:
                        save_kwargs["exif"] = exif

                    new_file = base + ".jpeg"
                    img.save(new_file, **save_kwargs)

                    return new_file, True

            return _, False

        return await asyncio.to_thread(work)

    except Exception as e:
        logger.error(e)
        raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_IMAGE_PREPROCESS_FAIL)


def basename_from_s3(url: str) -> str:
    p = urlparse(url)  # s3:// 스킴 분리
    return posixpath.basename(p.path)  # 마지막 경로 조각


def extract_order_from_filename(name: str) -> int | None:
    # 예: cat_3.jpeg, cat_03.jpeg, photo-12.png -> 3, 3, 12
    m = re.search(r"[_-](\d+)(?=\.[^.]+$)", name)
    return int(m.group(1)) if m else None


def pick_video_prompt_for_doc(s3_url: str, llm_result: dict) -> str:
    name = basename_from_s3(s3_url)
    n = extract_order_from_filename(name)  # 1-based 번호
    results = (llm_result or {}).get("results", [])
    if not results:
        raise ValueError("llm_result.results가 비어 있습니다.")
    if isinstance(n, int):
        # image_number 우선 매칭
        for item in results:
            if item.get("image_number") == n:
                return item.get("video_prompt", "")
        # 인덱스 백업 매칭
        idx = n - 1
        if 0 <= idx < len(results):
            return results[idx].get("video_prompt", "")
    # 폴백: 마지막 항목
    return results[-1].get("video_prompt", "")


async def webp_to_jpg(input_path: str, quality: int = 100):
    """
    WEBP 이미지를 JPG로 비동기 변환
    Args:
        input_path (str): 변환할 WEBP 파일 경로
        output_path (str): 저장할 JPG 파일 경로
        quality (int): JPEG 저장 품질 (1~100)
    """

    def convert():
        with Image.open(input_path) as img:
            # 투명 채널 처리
            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert("RGB")

            output_path = os.path.splitext(input_path)[0] + ".jpg"
            img.save(output_path, "JPEG", quality=quality, optimize=True)

            return output_path

    # 변환 작업을 스레드에서 실행
    return await asyncio.to_thread(convert)
