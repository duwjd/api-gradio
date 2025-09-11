import asyncio
import json
import logging
import os
import time
from copy import deepcopy
from itertools import cycle

import aiofiles
import replicate

from api.exceptions import response_error
from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis
from config.const import ANALYSIS_ERROR, API_VIDEO_MODEL, BaseErrorEnum
from utils.s3_util_engine import s3_file_exist, upload_s3
from utils.util import crop_image, encode_image_base64, open_image, resize_image

logger = logging.getLogger("app")
# 자동 export os.getenv("REPLICATE_API_TOKEN")
replicate_api_keys = [
    "r8_HETS7NHZtCVMyVGzXK3WqrZEYVwB7Ov2oPRqB",
    # "r8_376f23Cgw7uwTY3oKlYNfU6hThv3QbE06zYbB", # 크레잇 이슈
]
api_key_cycle = cycle(replicate_api_keys)


class VideoService:
    @staticmethod
    async def get_replicate_client():
        api_key = next(api_key_cycle)
        return replicate.Client(api_token=api_key)

    @staticmethod
    async def run_multiple_api(
        model: str,
        document_files: list,
        video_prompts: list,
        retry_timeout: int = 20,
        total_timeout: int = 4000,
    ):
        """
        모델 API 요청을 interval 간격으로 순차 시작, 병렬 처리
        """
        result = [None] * len(document_files)
        tasks = []

        async def run_video_api(
            i: int,
            document_file: str,
        ):
            """
            비디오 모델 api 요청
            """
            RETRY_LIMIT = 10
            retry_count = 0

            while retry_count < RETRY_LIMIT:
                try:
                    logger.info(f"비디오 생성 API 요청 시작: {model}")
                    video_info = await VideoService.video_api(
                        model,
                        document_file,
                        video_prompts[i],
                    )
                    result[i] = video_info
                    break

                except Exception as e:
                    error_detail = None
                    arg = e.args[0] if e.args else None

                    if isinstance(arg, BaseErrorEnum):
                        error_enum = arg
                        if len(e.args) > 1:
                            error_detail = e.args[1]
                    elif isinstance(arg, Exception):
                        error_detail = str(arg)

                    if (
                        error_enum.code
                        == ANALYSIS_ERROR.AI_API_ANALYSIS_SENSITIVE_IMAGE.code
                        or error_enum.code
                        == ANALYSIS_ERROR.AI_API_ANALYSIS_INVALID_PIXEL_IMAGE.code
                        or error_enum.code
                        == ANALYSIS_ERROR.AI_API_ANALYSIS_SEXUAL_IMAGE.code
                        or error_enum.code
                        == ANALYSIS_ERROR.AI_API_ANALYSIS_INVALID_CROPPED_PIXEL_IMAGE.code
                    ):
                        logger.error(f"재시도 중지: {e}")
                        raise Exception(error_enum, error_detail)

                    retry_count += 1
                    if retry_count >= RETRY_LIMIT:
                        logger.error(
                            f"재시도{retry_count}회 실패. 재시도 중지. {model} ({document_file})"
                        )
                        raise Exception(
                            ANALYSIS_ERROR.AI_API_ANALYSIS_REPLICATE_RETRY_LIMIT_EXCEEDED
                        )

                    logger.warning(
                        f"실패: {model} ({document_file}) - 재시도 {retry_count}회: {e}"
                    )

                    await asyncio.sleep(retry_timeout)

        async def run_parallel():
            """
            모델 api 요청 병렬 처리
            """
            try:
                for i, document_file in enumerate(document_files):
                    # api 요청 백그라운드 실행
                    task = asyncio.create_task(run_video_api(i, document_file))
                    tasks.append(task)
                    await asyncio.sleep(retry_timeout)
            except Exception as e:
                raise e

        async def run_tasks():
            """
            모델 api 테스크 처리
            """
            await run_parallel()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # 에러 발생 시 즉시 raise
            for e in results:
                if isinstance(e, Exception):
                    raise e

        try:
            # 실행 및 타임아웃 적용
            await asyncio.wait_for(run_tasks(), timeout=total_timeout)

            return result
        except asyncio.TimeoutError:
            logger.error(f"API 비디오 생성 timeout: {total_timeout}초 초과")
            raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_API_TIMEOUT)

        except Exception as e:
            logger.error(f"API 비디오 생성 중 에러: {e}", exc_info=True)
            raise e

    @staticmethod
    async def video_api(
        model: str,
        document_file: str,
        video_prompt: str,
    ):
        """
        video api 실행
        """
        try:
            image = await open_image(document_file)
            start_time: float = time.time()
            model_name: str = model.split("/")[-1]
            input_image_field_name = "image"

            # 모델별 request 정의
            match model:
                case API_VIDEO_MODEL.KLING_V2_1:
                    input = {
                        "mode": "standard",  # standard or pro
                        "prompt": video_prompt,
                        "negative_prompt": """
blurry, low resolution, pixelated, artifacts, noisy, distorted, overexposed, underexposed,
poor lighting, bad composition, out of frame, unnatural colors, unrealistic, oversaturated,
washed out, duplicate, cropped, watermark, text, logo, extra limbs, missing fingers,
deformed, mutated, low detail, low contrast, compression artifacts, stretched, warped
""",
                        "duration": 5,  # 5 or 10
                    }
                    image = await crop_image(image, target_ratio=9 / 16)
                    image = await resize_image(image, 720, 1280)
                    input_image_field_name = "start_image"
                case API_VIDEO_MODEL.HAILUO_02:
                    input = {
                        "prompt": video_prompt,
                        "prompt_optimizer": False,
                        "resolution": "768p",  # 768p or 1080p
                        "duration": 6,  # 6 or 10
                    }
                    input_image_field_name = "first_frame_image"
                case API_VIDEO_MODEL.SEEDANCE_1_LITE:
                    input = {
                        "prompt": video_prompt,
                        "duration": 5,  # 5 or 10
                        # "fps": 24, # 기본 24
                        # "seed": 42,
                        "image": base64_image,
                        "resolution": "720p",  # 720p or 480p
                        "aspect_ratio": "9:16",  # 16:9 or 9:16
                        # "camera_fixed": False,
                    }
                    input_image_field_name = "image"
                case API_VIDEO_MODEL.SEEDANCE_1_PRO:
                    input = {
                        "prompt": video_prompt,
                        "duration": 5,  # 5 or 10
                        # "fps": 24, # 기본 24
                        # "seed": 42,
                        "resolution": "1080p",  # 1080p or 480p
                        "aspect_ratio": "9:16",  # 16:9 or 9:16 100 x 100
                        # "camera_fixed": False,
                    }
                    input_image_field_name = "image"
                case _:
                    raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_MODEL_INVALID)

            # add base64 image to input
            base64_image: str = await encode_image_base64(image)
            input[input_image_field_name] = base64_image
            # 모델 실행
            client = await VideoService.get_replicate_client()
            output = await client.async_run(model, input=input)
            video_byte: bytes = await asyncio.to_thread(output.read)
            logger.info(
                f"model: {model_name} runtime : {round(time.time() - start_time,2)}초"
            )

            return video_byte

        except Exception as e:
            logger.error(f"모델 api 요청 오류 발생: {e}", exc_info=True)
            if "Content flagged for: sexual" in str(e):
                raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_SEXUAL_IMAGE)
            if "flagged as sensitive" in str(e):
                raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_SENSITIVE_IMAGE)
            if "Image pixel is invalid" in str(e):
                raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_INVALID_PIXEL_IMAGE)
            if "Image Cropping size invalid" in str(e):
                raise Exception(
                    ANALYSIS_ERROR.AI_API_ANALYSIS_INVALID_CROPPED_PIXEL_IMAGE,
                    ANALYSIS_ERROR.AI_API_ANALYSIS_INVALID_CROPPED_PIXEL_IMAGE.message
                    + str(e).split("Image Cropping size invalid")[1],
                )

            raise Exception(ANALYSIS_ERROR.AI_API_ANALYSIS_VIDEO_API_FAIL)

    @staticmethod
    async def upload_video(
        video_bytes: list[bytes],
        document_files: list[str],
        upload_dir: str,
        s3_path: str,
        analysisHttps: str,
    ):
        """
        비디오 업로드
        """
        video_urls = []
        for i, video_byte in enumerate(video_bytes):
            file = os.path.basename(document_files[i]).split(".")[0]
            file_name = f"{file}.mp4"

            # 파일 path 설정
            file_path = f"{upload_dir}/{file_name}"
            s3_key = f"{s3_path}videos/{file_name}"

            https_path = f"{analysisHttps}videos/{file_name}"

            # mp4 파일 저장
            async with aiofiles.open(f"{upload_dir}/{file_name}", "wb") as file:
                await file.write(video_byte)

            # s3 업로드
            await upload_s3(file_path, s3_key)
            video_urls.append(https_path)

        logger.info(f"비디오 업로드 완료: {video_urls}")
        return video_urls