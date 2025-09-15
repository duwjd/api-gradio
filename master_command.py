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


def master_kill_gunicorn_debug():
    """
    master Gunicorn 종료
    """
    invoke_process = f"invoke master --env={os.getenv('ENV')}"
    gunicorn_process = f"gemgem-ai-master-{os.getenv('ENV')}"

    subprocess.run(["pkill", "-9", "-f", invoke_process])
    subprocess.run(["pkill", "-9", "-f", gunicorn_process])


def master_kill_gunicorn():
    """
    master Gunicorn 종료 (서버)
    """
    try:
        env = os.getenv("ENV")
        pid_file = os.path.join(os.path.dirname(__file__), f"gunicorn-master-{env}.pid")

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


def master_start_gunicorn_debug():
    """
    master Gunicorn 디버그 실행 (stdout/stderr 핸들링 강화 버전)
    - stdout은 gemgem-ai-master.log + 콘솔
    - stderr는 error-master.log + gemgem-ai-master.log + 콘솔
    """
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "log"))
    os.makedirs(log_dir, exist_ok=True)

    gemgem_log_path = os.path.join(log_dir, "gemgem-ai-master.log")
    error_log_path = os.path.join(log_dir, "error-master.log")
    env = os.environ.copy()

    gunicorn_cmd = [
        "gunicorn",
        "-c",
        "config/gunicorn_master_config.py",
        "api:master_create_app()",
        "--name",
        f"gemgem-ai-master-{os.getenv('ENV')}",
    ]

    try:
        gemgem_log = open(gemgem_log_path, "a")
        error_log = open(error_log_path, "a")

        process = subprocess.Popen(
            gunicorn_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        stdout_targets = [gemgem_log, sys.stdout]
        stderr_targets = [
            error_log,
            gemgem_log,
            sys.stdout,
        ]

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
            logger.info(f"master Gunicorn 종료됨 (exit_code={exit_code})")
            t1.join()
            t2.join()
            gemgem_log.flush()
            error_log.flush()
            gemgem_log.close()
            error_log.close()

        threading.Thread(target=wait_for_gunicorn, daemon=True).start()

        logger.info(f"master Gunicorn 시작됨 (PID={process.pid})")

    except Exception as e:
        logger.error(f"master Gunicorn 실행 중 예외 발생 {e}", exc_info=True)


def master_start_gunicorn():
    """
    master Gunicorn 실행
    """
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "log"))
    os.makedirs(log_dir, exist_ok=True)

    gemgem_log_path = os.path.join(log_dir, "gemgem-ai-master.log")
    error_log_path = os.path.join(log_dir, "error-master.log")
    env = os.environ.copy()

    gunicorn_cmd = [
        "gunicorn",
        "-c",
        "config/gunicorn_master_config.py",
        "api:master_create_app()",
        "--name",
        f"gemgem-ai-master-{os.getenv('ENV')}",
    ]

    try:
        # 짧게 테스트용으로 실행 후 바로 종료 (생존 여부 확인용)
        test_proc = subprocess.Popen(
            gunicorn_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        try:
            _, test_stderr = test_proc.communicate(
                timeout=2
            )  # 2초 안에 끝나지 않으면 살아있다고 판단
        except subprocess.TimeoutExpired:
            test_proc.kill()  # 살아있으면 정상
            test_proc.wait()
            # 실행 성공 → 백그라운드로 진짜 실행
            with open(gemgem_log_path, "a", buffering=1) as log_file:
                subprocess.Popen(
                    gunicorn_cmd,
                    stdout=log_file,
                    stderr=log_file,
                    env=env,
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
            logger.error("master Gunicorn 실행 실패:\n" + stderr_text)
            return

    except Exception as e:
        logger.exception("master Gunicorn 실행 중 예외 발생")


def master_start_gunicorn_watchdog():
    """
    master Gunicorn 디버그 실행
    """
    subprocess.run(["./venv/bin/python", "master_gunicorn_watchdog.py"])
