import asyncio
import logging
import os
import platform
import signal
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.exceptions import exception_handler, validation_exception_handler
from api.modules import api_register_router
from api.modules.analysis.consumer.analysis_consumer_task_queue import (
    analysis_consumer_task_queue,
)
from api.modules.swagger.common_doc import remove_422_doc
from api.modules_master import master_register_router
from api.modules_master.consumer.master_consumer_task_queue import (
    master_api_consumer_task_queue,
    master_model_consumer_task_queue,
)
from api.modules_op import op_api_register_router
from api.version_json import get_version_str
from config.log_config import setup_logging
from config.sentry_config import sentry_flush, sentry_init
from database.mariadb.session import task_llm_progress_to_fail
from database.redis.redis_client import redis_client
from utils.google_util import _vision_client, genai_client
from utils.gpt_util import gpt_client
from utils.s3_util import s3_client


@asynccontextmanager
async def api_lifespan(app: FastAPI):
    """
    FastAPI 앱의 api lifespan 클라이언트 정의
    """
    if platform.system() == "Linux":
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    # 분석 요청 task
    asyncio.create_task(analysis_consumer_task_queue())

    try:
        # redis
        app.state.redis_client = redis_client()

        # gpt
        app.state.gpt_client = gpt_client()

        # s3
        app.state.s3_client = s3_client()

        # vision
        app.state.vision_client = _vision_client

        # gimini
        app.state.genai_client = genai_client()

        # sentry
        if os.getenv("ENV") != "local":
            sentry_init()
        yield

    except Exception as e:
        raise e

    finally:
        # redis close
        app.state.redis_client.close()

        # gpt close
        app.state.gpt_client.close()

        # s3 close
        app.state.s3_client.close()

        # sentry 강제 전송
        sentry_flush()


@asynccontextmanager
async def op_lifespan(app: FastAPI):
    """
    FastAPI 앱의 lifespan 클라이언트 정의
    """
    if platform.system() == "Linux":
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    try:
        # redis
        app.state.redis_client = redis_client()

        # gpt
        app.state.gpt_client = gpt_client()

        # s3
        app.state.s3_client = s3_client()

        # vision
        app.state.vision_client = _vision_client

        # gimini
        app.state.genai_client = genai_client()

        # sentry
        if os.getenv("ENV") != "local":
            sentry_init()
        yield

    except Exception as e:
        raise e

    finally:

        # redis close
        app.state.redis_client.close()

        # gpt close
        app.state.gpt_client.close()

        # s3 close
        app.state.s3_client.close()

        # sentry 강제 전송
        sentry_flush()

        sys.exit(0)


@asynccontextmanager
async def master_lifespan(app: FastAPI):
    """
    FastAPI 앱의 master lifespan 클라이언트 정의
    """
    if platform.system() == "Linux":
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

    # master api task 반복 처리
    asyncio.create_task(master_api_consumer_task_queue())

    # master model task 반복 처리
    asyncio.create_task(master_model_consumer_task_queue())

    try:
        # redis
        app.state.redis_client = redis_client()

        # gpt
        app.state.gpt_client = gpt_client()

        # s3
        app.state.s3_client = s3_client()

        # vision
        app.state.vision_client = _vision_client

        # gimini
        app.state.genai_client = genai_client()

        # sentry
        if os.getenv("ENV") != "local":
            sentry_init()
        yield

    except Exception as e:
        raise e

    finally:
        # redis close
        app.state.redis_client.close()

        # gpt close
        app.state.gpt_client.close()

        # s3 close
        app.state.s3_client.close()

        # sentry 강제 전송
        sentry_flush()


def create_app() -> FastAPI:
    """
    api FastAPI 앱 설정, 실행
    """
    try:
        log_file_name = "gemgem-ai.log"
        error_file_name = "error.log"

        setup_logging(log_file_name, error_file_name)
        logger = logging.getLogger("app")

        # task progress -> fail로 변경
        task_llm_progress_to_fail()

        app_description = """
        AI 문서 분석 포맷 문서
        https://10t1m.atlassian.net/wiki/spaces/P10K1M/pages/946208793/AI
        
        AI 분석 결과 포맷 문서
        https://10t1m.atlassian.net/wiki/spaces/P10K1M/pages/938770514/AI
        """
        app_version = get_version_str(
            os.path.join(os.path.dirname(__file__), "version.json"), format="display"
        )

        app = FastAPI(
            title="GEMGEM-AI-API" + "-" + os.getenv("ENV"),
            description=app_description,
            version=app_version,
            docs_url="/api/docs",  # Swagger UI 경로
            redoc_url=None,  # ReDoc 비활성화
            lifespan=api_lifespan,
        )

        app.openapi = lambda: remove_422_doc(app)

        # FastAPI 예외 처리
        app.add_exception_handler(Exception, exception_handler)
        app.add_exception_handler(RequestValidationError, validation_exception_handler)

        # API 등록
        app.include_router(api_register_router())
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

        logger.info(f"[uvicorn] gemgem-ai-api-gradio start")
        logger.info("[uvicorn] OS : " + platform.system())

        return app

    except Exception as error:
        # 예외 로그 출력
        logger.error(f"Application api startup error: {str(error)}", exc_info=True)

        # Gunicorn 프로세스를 강제 종료
        os.kill(os.getppid(), signal.SIGTERM)

        sys.exit(1)  # Gunicorn이 정상적으로 오류를 감지하고 종료되도록 함.


def op_create_app() -> FastAPI:
    """
    op-api FastAPI 앱 설정, 실행
    """
    try:
        log_file_name = "gemgem-ai-op.log"
        error_file_name = "error-op.log"

        setup_logging(log_file_name, error_file_name)
        logger = logging.getLogger("app")

        app_description = """
        AI OP-API 문서
        https://10t1m.atlassian.net/wiki/spaces/P10K1M/pages/955285608/OP+API
        
        """
        app_version = get_version_str(
            os.path.join(os.path.dirname(__file__), "version.json"), format="display"
        )

        app = FastAPI(
            title="GEMGEM-AI-MASTER" + "-" + os.getenv("ENV"),
            description=app_description,
            version=app_version,
            docs_url="/api/docs",  # Swagger UI 경로
            redoc_url=None,  # ReDoc 비활성화
            lifespan=op_lifespan,
        )

        app.openapi = lambda: remove_422_doc(app)

        # FastAPI 예외 처리
        app.add_exception_handler(Exception, exception_handler)
        app.add_exception_handler(RequestValidationError, validation_exception_handler)

        # API 등록
        app.include_router(op_api_register_router())
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

        logger.info(f"[uvicorn] gemgem-ai-op start")
        logger.info("[uvicorn] OS : " + platform.system())

        return app

    except Exception as error:
        # 예외 로그 출력
        logger.error(f"Application op-api startup error: {str(error)}", exc_info=True)

        # Gunicorn 프로세스를 강제 종료
        os.kill(os.getppid(), signal.SIGTERM)

        sys.exit(1)  # Gunicorn이 정상적으로 오류를 감지하고 종료되도록 함.


def master_create_app() -> FastAPI:
    """
    op-api FastAPI 앱 설정, 실행
    """
    try:
        log_file_name = "gemgem-ai-master.log"
        error_file_name = "error-master.log"

        setup_logging(log_file_name, error_file_name)
        logger = logging.getLogger("app")

        app_description = """
        AI MASTER 문서
        
        """
        app_version = get_version_str(
            os.path.join(os.path.dirname(__file__), "version.json"), format="display"
        )

        app = FastAPI(
            title="GEMGEM-AI-MASTER" + "-" + os.getenv("ENV"),
            description=app_description,
            version=app_version,
            docs_url="/api/docs",  # Swagger UI 경로
            redoc_url=None,  # ReDoc 비활성화
            lifespan=master_lifespan,
        )

        app.openapi = lambda: remove_422_doc(app)

        # FastAPI 예외 처리
        app.add_exception_handler(Exception, exception_handler)
        app.add_exception_handler(RequestValidationError, validation_exception_handler)

        # API 등록
        app.include_router(master_register_router())
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

        logger.info(f"[uvicorn] gemgem-ai-master start")
        logger.info("[uvicorn] OS : " + platform.system())

        return app

    except Exception as error:
        # 예외 로그 출력
        logger.error(f"Application master startup error: {str(error)}", exc_info=True)

        # Gunicorn 프로세스를 강제 종료
        os.kill(os.getppid(), signal.SIGTERM)
        sys.exit(1)  # Gunicorn이 정상적으로 오류를 감지하고 종료되도록 함.
