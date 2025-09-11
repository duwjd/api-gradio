import io
import logging
import mimetypes
import os
from contextlib import asynccontextmanager
from typing import Optional

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError

from api.modules.schema.aws_schema import (
    ReqDownloadS3PresignedUrl,
    ReqUploadS3PresignedUrl,
    ResUploadS3PresignedUrl,
)
from config.const import ANALYSIS_ERROR, S3

# 로거 설정
logger = logging.getLogger("app")


@asynccontextmanager
async def s3_client_async():
    """AWS S3 비동기 클라이언트 생성"""
    session = aioboto3.Session()
    config = Config(region_name="ap-northeast-2", s3={"addressing_style": "virtual"})

    async with session.client(
        "s3",
        region_name=os.environ.get("AWS_DEFAULT_REGION"),
        config=config,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    ) as client:
        yield client


async def download_s3(
    s3_path: str, local_download_dir: str, local_file_name: str
) -> Optional[str]:
    """
    s3 파일 다운로드

    Args:
        s3_path (str): 다운로드할 S3 파일 경로
        local_download_dir (str): 다운로드할 로컬 디렉토리
        local_file_name (str): 로컬 파일명

    Returns:
        Optional[str]: 다운로드된 파일의 로컬 경로
    """
    try:
        bucket = get_s3_bucket(s3_path)
        async with s3_client_async() as s3_client:
            s3_key = s3_path.split(bucket)[1][1:]

            file_path = os.path.join(local_download_dir, local_file_name)
            logger.info(f"파일 다운로드: {file_path}")
            response = await s3_client.get_object(Bucket=bucket, Key=s3_key)

            body = response["Body"]
            chunk_size = 1024 * 1024

            with open(file_path, "wb") as f:
                while True:
                    chunk = await body.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)

            return file_path

    except Exception as e:
        logger.error(f"S3 다운로드 오류: {e}", exc_info=True)
        raise Exception(ANALYSIS_ERROR.AI_API_FILE_DOWNLOAD_FAIL)


async def upload_s3(file_path: str, s3_path: str):
    """
    s3 파일 업로드

    Args:
        file_path (str): 업로드할 파일 경로
        s3_path (str): 업로드할 S3 파일 경로
    """

    async with s3_client_async() as s3_client:
        bucket = get_s3_bucket(s3_path)
        s3_key = s3_path.split(bucket)[1][1:]
        mime_type, _ = mimetypes.guess_type(file_path)

        await s3_client.upload_file(
            file_path,
            bucket,
            s3_key,
            ExtraArgs={"ContentType": mime_type, "CacheControl": "no-store"},
        )


async def delete_s3(s3_path: str):
    """
    s3 파일 삭제

    Args:
        s3_path (str): 삭제할 S3 파일 경로
    """
    async with s3_client_async() as s3_client:
        bucket = get_s3_bucket(s3_path)
        s3_key = s3_path.split(bucket)[1][1:]

        await s3_client.delete_object(
            Bucket=bucket,
            Key=s3_key,
        )


async def s3_file_exist(s3_path: str) -> bool:
    """
    S3에 파일이 존재하는지 확인

    Args:
        s3_path (str): S3 파일 경로

    Returns:
        bool: 파일이 존재하는지 확인
    """
    async with s3_client_async() as s3:
        try:
            bucket = get_s3_bucket(s3_path)
            s3_key = s3_path.split(bucket)[1][1:]
            is_exist = await s3.head_object(Bucket=bucket, Key=s3_key)
            if is_exist == True:
                return True

        except Exception as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                return False  # 파일 없음
            logger.error(f"S3 파일 찾기 오류: {s3_path}", exc_info=True)
            raise


async def download_s3_presigned_url(
    req_body: ReqDownloadS3PresignedUrl, expires_in: int = 60
) -> Optional[str]:
    """
    S3에 파일이 존재할 경우에만 presigned URL을 생성

    Args:
        req_body (ReqCreateS3PresignedUrl): 요청 데이터 (s3Path 포함)
        expires_in (int): Presigned URL 유효시간 (초)

    Returns:
        Optional[str]: 다운로드 가능한 presigned URL (파일 없으면 None)
    """
    async with s3_client_async() as s3_client:
        try:
            bucket = get_s3_bucket(req_body.s3Path)
            s3_key = req_body.s3Path.split(bucket)[1][1:]

            # S3에 실제로 객체가 존재하는지 먼저 확인
            await s3_client.head_object(Bucket=bucket, Key=s3_key)

            # 파일 존재 시 presigned URL 생성
            presignedUrl = await s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": bucket, "Key": s3_key},
                ExpiresIn=expires_in,
            )

            logger.info(f"S3 Presigned 다운로드 URL 생성 완료: {presignedUrl}")
            return presignedUrl

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404" or error_code == "NoSuchKey":
                logger.warning(f"S3 파일 존재하지 않음: {s3_key}")
                return None
            else:
                logger.error(f"S3 Presigned 다운로드 URL 생성 실패: {e}", exc_info=True)
                return None


async def upload_s3_presigned_url(req_body: ReqUploadS3PresignedUrl):
    """
    s3 presigned url 업로드

    Args:
        req_body (List[ReqUploadS3PresignedUrl]):
            presigned URL을 생성할 요청 리스트.
            각 항목은 업로드 대상 S3 경로(s3Path)와 MIME 타입(mimeType)을 포함합니다.

    Returns:
        ResUploadS3PresignedUrl: {"uploadUrl": "https://s3...","Content-Type": "application/pdf","Cache-Control": "no-store"}
    """
    ext = req_body.mimeType.strip().lower()

    if ext not in MIME_TYPE_MAP:
        raise ValueError(f"지원하지 않는 확장자 입니다.: {ext}")

    resolved_mime = MIME_TYPE_MAP[ext]
    async with s3_client_async() as s3_client:
        try:
            bucket = get_s3_bucket(req_body.s3Path)
            s3_key = req_body.s3Path.split(bucket)[1][1:]
            uploadUrl = await s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": bucket,
                    "Key": s3_key,
                    "ContentType": resolved_mime,
                    "CacheControl": "no-store",
                },
                ExpiresIn=600,
            )

            logger.info(f"S3 presigned 업로드 URL 생성 완료: {uploadUrl}")

            return ResUploadS3PresignedUrl(
                uploadUrl=uploadUrl,
                headers={
                    "Content-Type": resolved_mime,
                    "Cache-Control": "no-store",
                },
            )
        except Exception as e:
            logger.error(
                f"[S3 upload presigned-url] 업로드 URL 생성 실패: {e}", exc_info=True
            )
            raise


async def upload_s3_binary(
    bucket: str, s3_key: str, binary: bytes, mime_type: str
) -> str:
    """
    바이너리 데이터를 S3에 업로드

    Args:
        binary_data (bytes): 업로드할 파일의 바이너리 데이터
        s3_key (str): S3 내 저장 경로 (예: uploads/sample.mp3)
    """
    try:
        async with s3_client_async() as s3_client:
            file_obj = io.BytesIO(binary)
            file_obj.seek(0)

            await s3_client.put_object(
                Bucket=bucket, Key=s3_key, Body=binary, ContentType=mime_type
            )

            logger.info(f"[S3 업로드 완료] {S3.HTTPS}{s3_key}")
    except Exception as e:
        logger.error(f"S3 바이너리 업로드 오류: {e}", exc_info=True)
        raise


def get_s3_bucket(s3_key: str):
    return s3_key.split("/")[2]


def get_public_https_to_s3_key(bucket: str, url: str):
    """
    public s3 https -> s3 key 변환
    """

    return (
        "s3://"
        + bucket
        + url.split(f"https://{bucket}.s3.{S3.REGION}.amazonaws.com")[1]
    )


def get_private_s3_key_to_https(analysisS3: str, analysisHttps: str, url: str):
    """
    private s3 key -> s3 https 변환
    """
    s3_key = url.split(analysisS3)[1]
    return analysisHttps + s3_key


# MIME 타입 매핑
MIME_TYPE_MAP = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "txt": "text/plain",
    "csv": "text/csv",
    "json": "application/json",
    "xml": "application/xml",
    "zip": "application/zip",
    "mp4": "video/mp4",
    "mp3": "audio/mpeg",
    "webp": "image/webp",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
