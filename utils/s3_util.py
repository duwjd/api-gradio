import base64
import io
import logging
import mimetypes
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from fastapi import Request

# 로거 설정
logger = logging.getLogger("app")


def s3_client() -> BaseClient:
    """AWS S3 클라이언트 반환"""
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_DEFAULT_REGION"),
    )


def get_s3_client(req_app: Request):
    """
    S3 클라이언트 가져오기

    Args:
        req_app (Request): FastAPI의 요청 객체

    Returns:
        BaseClient: S3 클라이언트
    """
    s3_client: BaseClient = req_app.app.state.s3_client
    if s3_client is None:
        raise RuntimeError("S3 클라이언트가 초기화되지 않았습니다.")
    return s3_client


def upload_files(req_app: Request, folder_path: str, s3_folder_path: str):
    """
    지정한 폴더 내의 모든 파일을 S3에 업로드합니다.

    Args:
        req_app (Request): FastAPI의 요청 객체
        folder_path (str): 업로드할 로컬 폴더 경로
        s3_path (str): S3 대상 디렉토리 경로

    Returns:
        List[str]: 업로드에 성공한 파일들의 S3 경로 리스트
    """

    logger.info(f"S3 업로드 시작: {folder_path} -> {s3_folder_path}")
    try:
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            Exception(f"업로드할 폴더 없음: {folder_path}")

        for file in folder.iterdir():
            if file.is_file():

                logger.info(f"S3 업로드 파일 이름 : {file.name}")
                s3_path = s3_folder_path + file.name
                upload_file(req_app, str(file), s3_path)

    except Exception as e:
        logger.error(f"S3 업로드 실패: {e}", exc_info=True)
        raise e


def upload_file(local_file_path: str, s3_path: str) -> bool:
    """
    로컬 파일을 S3에 업로드합니다.
    Args:
        req_app (Request): FastAPI의 요청 객체
        local_file_path (str): 업로드할 로컬 파일 경로
        s3_path (str): S3 대상 경로 (예: "s3://my-bucket/uploads/file.txt")
    Returns:
        bool: 업로드 성공 여부 (True/False)
    Example:
        >>> upload_file(s3_client, "local.txt", "s3://my-bucket/local.txt")
    """
    client = s3_client()
    parsed_url = urlparse(s3_path)
    s3_bucket = parsed_url.netloc
    s3_key = parsed_url.path.lstrip("/")

    mime_type, _ = mimetypes.guess_type(local_file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    try:
        client.upload_file(
            local_file_path,
            s3_bucket,
            s3_key,
            ExtraArgs={"ContentType": mime_type, "CacheControl": "no-store"},
        )
        logger.info(f"S3 업로드 완료 {s3_path}")

        return True
    except ClientError as e:
        logger.error(f"S3 업로드 오류: {e}")

        return False


def download_from_s3(
    req_app: Request, s3_path: str, local_download_dir: str, local_file_name: str
) -> Optional[str]:
    """
    S3에서 파일을 다운로드합니다.
    Args:
        req_app (Request): FastAPI의 요청 객체
        s3_path (str): S3 파일 경로 (예: "s3://my-bucket/sample.pdf")
        local_download_dir (str): 다운로드할 로컬 디렉토리
        local_file_name (str): 저장할 로컬 파일명
    Returns:
        Optional[str]: 다운로드된 파일의 로컬 경로 (실패 시 None)
    Example:
        >>> download_from_s3("s3://my-bucket/sample.pdf", "/tmp", "sample")
    """
    try:
        s3_client = get_s3_client(req_app)
        parsed_url = urlparse(s3_path)
        s3_bucket = parsed_url.netloc
        s3_key = parsed_url.path.lstrip("/")

        tmp_uploaded_file = os.path.join(
            local_download_dir, local_file_name + os.path.splitext(s3_path)[1]
        )  # 확장자 추가

        s3_client.download_file(s3_bucket, s3_key, tmp_uploaded_file)

        return tmp_uploaded_file
    except Exception as e:
        logger.error(f"S3 다운로드 오류: {e}")
        raise


def copy_s3_file(
    req_app: Request, source_s3_path: str, target_s3_path: str
) -> Optional[str]:
    """
    S3 내에서 파일을 복사합니다.
    Args:
        req_app (Request): FastAPI의 요청 객체
        source_s3_path (str): 원본 S3 파일 경로 (예: "s3://my-bucket/uploads/sample.pdf")
        target_s3_path (str): 복사할 대상 S3 파일 경로 (예: "s3://my-bucket/backups/sample.pdf")
    Returns:
        Optional[str]: 복사된 대상 경로 (성공 시), None (실패 시)
    Example:
        >>> copy_s3_file("s3://my-bucket/uploads/sample.pdf", "s3://my-bucket/backups/sample.pdf")
    """
    try:
        s3_client = get_s3_client(req_app)
        source_url = urlparse(source_s3_path)
        target_url = urlparse(target_s3_path)

        source_bucket = source_url.netloc
        source_key = source_url.path.lstrip("/")
        target_bucket = target_url.netloc
        target_key = target_url.path.lstrip("/")

        copy_source = {"Bucket": source_bucket, "Key": source_key}
        s3_client.copy(copy_source, target_bucket, target_key)

        logger.info(f"File copied from {source_s3_path} to {target_s3_path}")
        return target_s3_path
    except Exception as e:
        logger.error(f"S3 파일 복사 오류: {e}")
        return None


# def get_public_s3_https(key: str):
#     key = key.split("gemgem-public-10k1m/")[1]

#     return f"https://gemgem-public-10k1m.s3.ap-northeast-2.amazonaws.com/{key}"


def upload_base64(req_body: str, req_app: Request, s3_path: str) -> bool:
    """
    base64 데이터를 S3에 업로드합니다.

    Args:
        req_body (str): base64 인코딩된 파일 데이터 (data URI 가능)
        req_app (Request): FastAPI 요청 객체 (S3 client 추출용)
        s3_path (str): S3 대상 경로 (예: "s3://my-bucket/uploads/image.png")

    Returns:
        bool: 업로드 성공 여부
    """
    s3_client = get_s3_client(req_app)
    parsed_url = urlparse(s3_path)
    s3_bucket = parsed_url.netloc
    s3_key = parsed_url.path.lstrip("/")

    # base64 헤더 분리 (있을 수도 있음)
    if "," in req_body:
        _, b64_data = req_body.split(",", 1)
    else:
        b64_data = req_body

    try:
        # base64 디코딩 → 메모리 버퍼
        file_bytes = base64.b64decode(b64_data)
        file_stream = io.BytesIO(file_bytes)

        # MIME 타입 추정
        mime_type, _ = mimetypes.guess_type(s3_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        # S3 업로드
        s3_client.upload_fileobj(
            Fileobj=file_stream,
            Bucket=s3_bucket,
            Key=s3_key,
            ExtraArgs={"ContentType": mime_type, "CacheControl": "no-store"},
        )

        logger.info(f"✅ S3 업로드 성공: {s3_path}")
        return True

    except (ClientError, Exception) as e:
        logger.error(f"S3 업로드 실패: {e}")
        return False
