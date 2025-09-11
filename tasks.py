import asyncio
import logging
import os
import sys

from invoke import task

from api_command import (
    api_db_revision,
    api_db_upgrade,
    api_kill_gunicorn,
    api_kill_gunicorn_debug,
    api_start_gunicorn,
    api_start_gunicorn_watchdog,
)
from config.env_config import load_environment
from config.log_config import setup_logging
from master_command import (
    master_kill_gunicorn,
    master_kill_gunicorn_debug,
    master_start_gunicorn,
    master_start_gunicorn_watchdog,
)
from op_api_command import (
    op_api_kill_gunicorn,
    op_api_kill_gunicorn_debug,
    op_api_start_gunicorn,
    op_api_start_gunicorn_watchdog,
    op_db_revision,
    op_db_upgrade,
)

from gradio_command import (
    gradio_kill_gunicorn,
    gradio_kill_gunicorn_debug,
    gradio_start_gunicorn,
    gradio_start_gunicorn_watchdog,
)

API_ENVS = {"local", "development", "staging", "product"}
OP_API_ENVS = {"local", "development", "operation"}
GRADIO_ENVS = {"local"}


@task(name="api")
def gemgem_api(c, debug=False, env=""):
    """
    api Gunicorn 실행 (local, development, staging, product 중 선택)

    Example:
        invoke api --env=local
        invoke api --env=local --debug (디버그 모드 파일 변경 시 서버 재시작)
    """

    try:
        setup_logging()
        env = env.strip().lower()  # 공백 제거 및 소문자로 변환
        logger = logging.getLogger("app")

        if env not in API_ENVS:
            logger.error(f"Invalid environment: '{env}'")
            logger.error(f"Available environments: {', '.join(API_ENVS)}")
            sys.exit(1)  # 잘못된 환경 값이면 즉시 종료

        os.environ["ENV"] = env
        load_environment()

        # from api.modules.task.task_llm_rotate import background_llm_rotate

        # # LLM 우선순위 변경
        # background_llm_rotate()

        if debug:
            os.environ["DEBUG"] = "true"
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

            # gunicorn 프로세스 종료
            api_kill_gunicorn_debug()

            # api db 마이그레이션 파일 생성, 변경 사항 적용
            api_db_revision()
            api_db_upgrade()

            # debug 모드 실행
            api_start_gunicorn_watchdog()

        else:
            # 운영 환경 실행
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            api_kill_gunicorn()

            # db 변경 사항 적용
            api_db_upgrade()

            api_start_gunicorn()

    except Exception as e:
        logger.error(f"Error api task: {e}", exc_info=True)
        raise e


@task(name="op-api")
def op_api(c, debug=False, env=""):
    """
    op_api Gunicorn 실행 (local, development, operation 중 선택)

    Example:
        invoke op-api --env=local
        invoke op-api --env=local --debug (디버그 모드 파일 변경 시 서버 재시작)
    """

    try:
        setup_logging()
        env = env.strip().lower()  # 공백 제거 및 소문자로 변환
        logger = logging.getLogger("app")

        if env not in OP_API_ENVS:
            logger.error(f"Available environments: {', '.join(OP_API_ENVS)}")
            sys.exit(1)  # 잘못된 환경 값이면 즉시 종료

        os.environ["ENV"] = env
        load_environment()

        if debug:
            os.environ["DEBUG"] = "true"
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            # gunicorn 프로세스 종료
            op_api_kill_gunicorn_debug()

            # op db 마이그레이션 파일 생성, 변경 사항 적용
            op_db_revision()
            op_db_upgrade()

            # debug 모드 실행
            op_api_start_gunicorn_watchdog()

        else:
            # 운영 환경 실행
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            op_api_kill_gunicorn()

            # db 변경 사항 적용
            op_db_upgrade()

            op_api_start_gunicorn()

    except Exception as e:
        logger.error(f"Error op-api task: {e}", exc_info=True)
        raise e


@task(name="master")
def master(c, debug=False, env=""):
    """
    master Gunicorn 실행 (local, development, staging, product 중 선택)

    Example:
        invoke master --env=local
        invoke master --env=local --debug (디버그 모드 파일 변경 시 서버 재시작)
    """

    try:
        setup_logging()
        env = env.strip().lower()  # 공백 제거 및 소문자로 변환
        logger = logging.getLogger("app")

        if env not in API_ENVS:
            logger.error(f"Invalid environment: '{env}'")
            logger.error(f"Available environments: {', '.join(API_ENVS)}")
            sys.exit(1)  # 잘못된 환경 값이면 즉시 종료

        os.environ["ENV"] = env
        load_environment()

        from api.modules_master.consumer.task_queue import master_task_sqs_queue

        # sqs_queue task 반복 처리
        master_task_sqs_queue()

        if debug:
            os.environ["DEBUG"] = "true"
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

            # gunicorn 프로세스 종료
            master_kill_gunicorn_debug()

            # debug 모드 실행
            master_start_gunicorn_watchdog()

        else:
            # 운영 환경 실행
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            master_kill_gunicorn()
            master_start_gunicorn()

    except Exception as e:
        logger.error(f"Error master task: {e}", exc_info=True)
        raise e


@task(name="gradio")
def gradio(c, debug=False,env=""):
    """
    gradio Gunicorn 실행 (local, development, staging, product 중 선택)

    Example:
        invoke gradio --env=local
    """

    try:
        setup_logging()
        env = env.strip().lower()  # 공백 제거 및 소문자로 변환
        logger = logging.getLogger("app")

        if env not in GRADIO_ENVS:
            logger.error(f"Invalid environment: '{env}'")
            logger.error(f"Available environments: {', '.join(GRADIO_ENVS)}")
            sys.exit(1)  # 잘못된 환경 값이면 즉시 종료

        os.environ["ENV"] = env
        load_environment()

        if debug:
            os.environ["DEBUG"] = "true"
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

            # gunicorn 프로세스 종료
            gradio_kill_gunicorn_debug()

            # api db 마이그레이션 파일 생성, 변경 사항 적용
            api_db_revision()
            api_db_upgrade()

            # debug 모드 실행
            gradio_start_gunicorn_watchdog()

        else:
            # 운영 환경 실행
            os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

            gradio_kill_gunicorn()

            # db 변경 사항 적용
            api_db_upgrade()

            gradio_start_gunicorn()

    except Exception as e:
        logger.error(f"Error api task: {e}", exc_info=True)
        raise e