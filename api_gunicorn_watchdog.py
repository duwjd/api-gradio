import hashlib
import logging
import os
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from api_command import (
    api_db_revision,
    api_db_upgrade,
    api_kill_gunicorn_debug,
    api_start_gunicorn_debug,
)
from config.log_config import setup_logging

file_hashes = {}

setup_logging("gemgem-ai.log", "error.log")
logger = logging.getLogger("app")


def get_file_hash(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


WATCHED_DIRS = [os.path.abspath(".")]


class RestartGunicornHandler(FileSystemEventHandler):
    def on_modified(self, event):
        try:
            if event.is_directory:
                return

            if not event.src_path.endswith(".py"):
                return

            # 파일이 아직 저장 도중일 수 있으니 잠깐 대기
            time.sleep(0.1)

            # 새 해시 계산
            new_hash = get_file_hash(event.src_path)
            if new_hash is None:
                return

            # 이전 해시 가져오기
            old_hash = file_hashes.get(event.src_path)

            # 해시 비교
            if old_hash == new_hash:
                logger.info(f"파일 내용 변경 없음: {event.src_path}")
                return

            # 내용이 변경된 경우
            file_hashes[event.src_path] = new_hash  # 해시 갱신
            logger.info(f"파일 변경 감지됨: {event.src_path} → Gunicorn 재시작")

            # gunicorn 프로세스 종료
            api_kill_gunicorn_debug()

            # api db 마이그레이션 파일 생성, 변경 사항 적용
            api_db_revision()
            api_db_upgrade()

            # debug 모드 실행
            api_start_gunicorn_debug()

        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    api_start_gunicorn_debug()

    observer = Observer()
    event_handler = RestartGunicornHandler()

    for directory in WATCHED_DIRS:
        if os.path.exists(directory):
            observer.schedule(event_handler, path=directory, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        api_kill_gunicorn_debug()
    observer.join()
