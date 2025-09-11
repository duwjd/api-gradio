import os
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from config.env_config import load_environment

load_environment()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_DATABASE = os.environ.get("DB_DATABASE")
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "100"))

DB_HOST_DEV = os.environ.get("DB_HOST_DEV")
DB_PORT_DEV = int(os.environ.get("DB_PORT_DEV", "3306"))
DB_USER_DEV = os.environ.get("DB_USER_DEV")
DB_PASSWORD_DEV = os.environ.get("DB_PASSWORD_DEV")
DB_DATABASE_DEV = os.environ.get("DB_DATABASE_DEV")
DB_POOL_SIZE_DEV = int(os.environ.get("DB_POOL_SIZE_DEV", "100"))

DB_HOST_STG = os.environ.get("DB_HOST_STG")
DB_PORT_STG = int(os.environ.get("DB_PORT_STG", "3306"))
DB_USER_STG = os.environ.get("DB_USER_STG")
DB_PASSWORD_STG = os.environ.get("DB_PASSWORD_STG")
DB_DATABASE_STG = os.environ.get("DB_DATABASE_STG")
DB_POOL_SIZE_STG = int(os.environ.get("DB_POOL_SIZE_STG", "100"))

DB_HOST_PRD = os.environ.get("DB_HOST_PRD")
DB_PORT_PRD = int(os.environ.get("DB_PORT_PRD", "3306"))
DB_USER_PRD = os.environ.get("DB_USER_PRD")
DB_PASSWORD_PRD = os.environ.get("DB_PASSWORD_PRD")
DB_DATABASE_PRD = os.environ.get("DB_DATABASE_PRD")
DB_POOL_SIZE_PRD = int(os.environ.get("DB_POOL_SIZE_PRD", "100"))

DB_HOST_OP = os.environ.get("DB_HOST_OP")
DB_PORT_OP = int(os.environ.get("DB_PORT_OP", "3306"))
DB_USER_OP = os.environ.get("DB_USER_OP")
DB_PASSWORD_OP = os.environ.get("DB_PASSWORD_OP")
DB_DATABASE_OP = os.environ.get("DB_DATABASE_OP")
DB_POOL_SIZE_OP = int(os.environ.get("DB_POOL_SIZE_OP", "100"))


ASYNC_DATABASE_URL = (
    f"mariadb+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
)
ASYNC_DATABASE_URL_DEV = (
    f"mariadb+asyncmy://{DB_USER_DEV}:{DB_PASSWORD_DEV}@{DB_HOST_DEV}/{DB_DATABASE_DEV}"
)

ASYNC_DATABASE_URL_STG = (
    f"mariadb+asyncmy://{DB_USER_STG}:{DB_PASSWORD_STG}@{DB_HOST_STG}/{DB_DATABASE_STG}"
)

ASYNC_DATABASE_URL_PRD = (
    f"mariadb+asyncmy://{DB_USER_PRD}:{DB_PASSWORD_PRD}@{DB_HOST_PRD}/{DB_DATABASE_PRD}"
)

ASYNC_DATABASE_URL_OP = (
    f"mariadb+asyncmy://{DB_USER_OP}:{DB_PASSWORD_OP}@{DB_HOST_OP}/{DB_DATABASE_OP}"
)


# 비동기 엔진 생성
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=DB_POOL_SIZE,  # 연결 수
    max_overflow=10,  # 임시 추가 연결 수
    pool_timeout=30,  # timeout 30초
    pool_recycle=1800,  # 재연결 확인 30분
    pool_pre_ping=True,  # 연결 끊김 방지
)

# dev 비동기 엔진 생성
async_engine_dev = create_async_engine(
    ASYNC_DATABASE_URL_DEV,
    pool_size=DB_POOL_SIZE_DEV,  # 연결 수
    max_overflow=10,  # 임시 추가 연결 수
    pool_timeout=30,  # timeout 30초
    pool_recycle=1800,  # 재연결 확인 30분
    pool_pre_ping=True,  # 연결 끊김 방지
)

# stg 비동기 엔진 생성
async_engine_stg = create_async_engine(
    ASYNC_DATABASE_URL_STG,
    pool_size=DB_POOL_SIZE_STG,  # 연결 수
    max_overflow=10,  # 임시 추가 연결 수
    pool_timeout=30,  # timeout 30초
    pool_recycle=1800,  # 재연결 확인 30분
    pool_pre_ping=True,  # 연결 끊김 방지
)

# prd 비동기 엔진 생성
async_engine_prd = create_async_engine(
    ASYNC_DATABASE_URL_PRD,
    pool_size=DB_POOL_SIZE_PRD,  # 연결 수
    max_overflow=10,  # 임시 추가 연결 수
    pool_timeout=30,  # timeout 30초
    pool_recycle=1800,  # 재연결 확인 30분
    pool_pre_ping=True,  # 연결 끊김 방지
)

# op 비동기 엔진 생성
async_engine_op = create_async_engine(
    ASYNC_DATABASE_URL_OP,
    pool_size=DB_POOL_SIZE_OP,  # 연결 수
    max_overflow=10,  # 임시 추가 연결 수
    pool_timeout=30,  # timeout 30초
    pool_recycle=1800,  # 재연결 확인 30분
    pool_pre_ping=True,  # 연결 끊김 방지
)


# DB session 생성
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# dev DB session 생성
AsyncSessionDev = async_sessionmaker(
    bind=async_engine_dev,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# stg DB session 생성
AsyncSessionStg = async_sessionmaker(
    bind=async_engine_stg,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# prd DB session 생성
AsyncSessionPrd = async_sessionmaker(
    bind=async_engine_prd,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# op DB session 생성
AsyncSessionOp = async_sessionmaker(
    bind=async_engine_op,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


SYNC_DATABASE_URL = f"mariadb+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"

# 동기 엔진 생성
sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True, pool_timeout=60)

# DB session 생성
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)
