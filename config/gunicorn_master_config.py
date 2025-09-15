import fcntl
import os
import sys
from datetime import datetime

from config.env_config import load_environment

# 환경 변수 로드 및 gevent 패치
load_environment()
PORT = os.getenv("GUNICORN_MASTER_PORT")
ENV = os.getenv("ENV").lower()

# Gunicorn 기본 설정
bind = f"0.0.0.0:{PORT}"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 10000
keepalive = 5
preload_app = True  # Master가 앱 실행 후, Worker들이 복사하여 실행
reload = True
accesslog = None
# Gunicorn stdout/stderr 버퍼링 해제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

# Gunicorn 옵션
capture_output = True  # stdout/stderr → gunicorn 로그로 캡처
enable_stdio_inheritance = True  # 자식 프로세스도 stdout 공유

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PID_FILE_PATH = os.path.join(BASE_DIR, f"gunicorn-master-{ENV}.pid")


# PID 파일이 없으면 새로 생성
if not os.path.exists(PID_FILE_PATH):
    with open(PID_FILE_PATH, "w") as f:
        pass  # 파일 생성만

# 마스터 PID 저장
pidfile = PID_FILE_PATH  # gunicorn 기본 pidfile 지정


# 워커 PID도 같은 파일에 append 저장
def post_fork(server, worker):
    with open(PID_FILE_PATH, "a") as f:
        # 파일 잠금 처리 (여러 워커에서 동시에 접근할 경우 안전성 확보)
        fcntl.flock(
            f, fcntl.LOCK_EX
        )  # 배타적 잠금 (다른 프로세스가 동시에 접근하지 못하도록)
        f.write(f"{worker.pid}\n")
        fcntl.flock(f, fcntl.LOCK_UN)  # 잠금 해제


log_dir = os.path.abspath("log")
os.makedirs(log_dir, exist_ok=True)

today_str = datetime.now().strftime("%Y-%m-%d")

log_files = {
    "gemgem-ai-master": "gemgem-ai-master.log",
    "error-master": "error-master.log",
}

for name, filename in log_files.items():
    full_path = os.path.join(log_dir, filename)

    # (1) 기존 로그 파일이 있을 경우 → 날짜 지난 경우 리네임
    if os.path.exists(full_path):
        # 마지막 수정 날짜 추출
        last_modified = datetime.fromtimestamp(os.path.getmtime(full_path))
        last_modified_str = last_modified.strftime("%Y-%m-%d")

        if last_modified_str != today_str:
            archived_name = f"{filename}.{last_modified_str}"
            archived_path = os.path.join(log_dir, archived_name)

            # 기존 파일을 날짜 붙여서 리네임
            os.rename(full_path, archived_path)

    # (2) 오늘 날짜 파일이 없다면 새로 생성
    if not os.path.exists(full_path):
        open(full_path, "a").close()
