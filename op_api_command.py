import logging
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
import threading
from utils.util import stream_and_tee

logger = logging.getLogger("app")


def op_api_kill_gunicorn_debug():
    """
    op-api Gunicorn 종료
    """
    invoke_process = f"invoke op-api --env={os.getenv('ENV')}"
    gunicorn_process = f"gemgem-ai-op-{os.getenv('ENV')}"

    subprocess.run(["pkill", "-9", "-f", invoke_process])
    subprocess.run(["pkill", "-9", "-f", gunicorn_process])


def op_api_kill_gunicorn():
    """
    op-api Gunicorn 종료 (서버)
    """
    try:
        env = os.getenv("ENV")
        pid_file = os.path.join(os.path.dirname(__file__), f"gunicorn-{env}.pid")

        if not os.path.exists(pid_file):
            logger.debug(f"PID file not found: {pid_file}")
            return

        # PID 파일 읽기
        with open(pid_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            logger.debug("PID file is empty.")
            return

        pids = []
        for line in lines:
            pid = int(line)
            pids.append(pid)

        logger.info(f"gunicorn processes: {pids}")

        # 프로세스 종료 및 PID 파일 수정
        remaining_pids = []
        with open(pid_file, "w") as f:
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGTERM)  # SIGTERM 신호로 프로세스 종료
                    logger.info(f"Killed PID: {pid}")
                except ProcessLookupError:
                    logger.info(f"PID {pid} not found (already terminated).")
                    continue  # 이미 종료된 프로세스는 무시하고 계속 진행

                # 종료된 프로세스의 PID는 파일에서 제거하지 않음
                # 파일에서 PID를 제거하고, 실행 중인 PID만 파일에 다시 기록
                remaining_pids.append(pid)

            # 남은 실행 중인 PID만 파일에 기록
            for pid in remaining_pids:
                f.write(f"{pid}\n")

    except Exception as e:
        logger.error(f"Error killing processes: {e}")


def op_api_start_gunicorn_debug():
    """
    op-api Gunicorn 디버그 실행 (stdout/stderr 핸들링 강화 버전)
    - stdout은 gemgem-ai.log + 콘솔
    - stderr는 error-op.log + gemgem-ai-op.log + 콘솔
    """
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "log"))
    os.makedirs(log_dir, exist_ok=True)

    gemgem_log_path = os.path.join(log_dir, "gemgem-ai-op.log")
    error_log_path = os.path.join(log_dir, "error-op.log")

    gunicorn_cmd = [
        "gunicorn",
        "-c",
        "config/gunicorn_op_api_config.py",
        "api:op_create_app()",
        "--name",
        f"gemgem-ai-op-{os.getenv('ENV')}",
    ]

    try:
        gemgem_log = open(gemgem_log_path, "a")
        error_log = open(error_log_path, "a")

        process = subprocess.Popen(
            gunicorn_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout_targets = [gemgem_log, sys.stdout]
        stderr_targets = [
            error_log,
            gemgem_log,
            sys.stdout,
        ]  # stderr → error.log + gemgem-ai.log + 콘솔

        # stdout tee
        t1 = threading.Thread(
            target=stream_and_tee,
            args=(process.stdout, stdout_targets),
            daemon=True,
        )

        # stderr tee
        t2 = threading.Thread(
            target=stream_and_tee,
            args=(process.stderr, stderr_targets),
            daemon=True,
        )

        t1.start()
        t2.start()

        def wait_for_gunicorn():
            exit_code = process.wait()
            logger.info(f"op Gunicorn 종료됨 (exit_code={exit_code})")
            t1.join()
            t2.join()
            gemgem_log.flush()
            error_log.flush()
            gemgem_log.close()
            error_log.close()

        threading.Thread(target=wait_for_gunicorn, daemon=True).start()

        logger.info(f"op-api Gunicorn 시작됨 (PID={process.pid})")

    except Exception as e:
        logger.error(f"op-api Gunicorn 실행 중 예외 발생 {e}", exc_info=True)


def op_api_start_gunicorn():
    """
    op-api Gunicorn 실행
    """
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "log"))
    os.makedirs(log_dir, exist_ok=True)

    gemgem_log_path = os.path.join(log_dir, "gemgem-ai-op.log")
    error_log_path = os.path.join(log_dir, "error-op.log")

    gunicorn_cmd = [
        "gunicorn",
        "-c",
        "config/gunicorn_op_api_config.py",
        "api:op_create_app()",
        "--name",
        f"gemgem-ai-op-{os.getenv('ENV')}",
    ]

    try:
        # 짧게 테스트용으로 실행 후 바로 종료 (생존 여부 확인용)
        test_proc = subprocess.Popen(
            gunicorn_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            _, test_stderr = test_proc.communicate(
                timeout=2
            )  # 2초 안에 끝나지 않으면 살아있다고 판단
        except subprocess.TimeoutExpired:
            test_proc.kill()  # 살아있으면 정상
            test_proc.wait()
            # 실행 성공 → 백그라운드로 진짜 실행
            with open(gemgem_log_path, "a") as log_file:
                subprocess.Popen(
                    gunicorn_cmd,
                    stdout=log_file,
                    stderr=log_file,
                )
            return

        # 2초 안에 죽었고, stderr 내용 있으면 실패 처리
        if test_proc.returncode != 0 and test_stderr:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            stderr_text = test_stderr.decode()
            with open(gemgem_log_path, "a") as log_file, open(
                error_log_path, "a"
            ) as err_file:
                log_file.write(f"{timestamp}{stderr_text}")
                err_file.write(f"{timestamp}{stderr_text}")
            logger.error("op Gunicorn 실행 실패:\n" + stderr_text)
            return

    except Exception as e:
        logger.exception("op Gunicorn 실행 중 예외 발생")


def op_api_start_gunicorn_watchdog():
    """
    op-api Gunicorn 디버그 실행
    """
    subprocess.run(["./venv/bin/python", "op_api_gunicorn_watchdog.py"])


def op_db_revision():
    """
    op 마이그레이션 파일 생성 (변경 사항 없으면 리비전 파일 삭제)
    """
    before_creation = time.time()

    subprocess.run(
        [
            "alembic",
            "-c",
            "alembic_op.ini",
            "revision",
            "--autogenerate",
            "-m",
            "auto",
        ],
        stdout=subprocess.DEVNULL,
    )

    versions_dir = os.path.join(os.path.dirname(__file__), "alembic_op", "versions")

    latest_file = max(
        (
            os.path.join(versions_dir, f)
            for f in os.listdir(versions_dir)
            if f.endswith(".py")
        ),
        key=os.path.getctime,
        default=None,
    )

    if latest_file and os.path.getctime(latest_file) >= before_creation - 1:
        with open(latest_file, "r", encoding="utf-8") as f:
            content = f.read()

        # upgrade/downgrade 모두 pass만 있는지 검사
        is_empty_upgrade = re.search(
            r"def upgrade\(\).*?:\s*(#.*\n)*\s*pass\s*(#.*)?", content, re.DOTALL
        )
        is_empty_downgrade = re.search(
            r"def downgrade\(\).*?:\s*(#.*\n)*\s*pass\s*(#.*)?", content, re.DOTALL
        )

        if is_empty_upgrade and is_empty_downgrade:
            os.remove(latest_file)
            logger.info("[Alembic Revision] OP DB 변경 없음 → 파일 삭제")
            return None
        else:
            logger.info(f"[Alembic Revision] OP DB 변경 확인: {latest_file}")
            return latest_file

    return None


def op_db_upgrade():
    """
    op 마이그레이션 최신 적용
    """
    subprocess.run(["alembic", "-c", "alembic_op.ini", "upgrade", "head"])
