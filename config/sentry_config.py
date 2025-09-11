import sentry_sdk
import os

from sentry_sdk.transport import HttpTransport

SENTRY_DSN = os.environ.get("SENTRY_DSN")


def sentry_init():
    """
    센트리 클라이언트 초기화
    """
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        transport=HttpTransport,
        environment=os.getenv("ENV"),
        debug=False,  # Sentry 디버그 로그 비활성화
    )


def sentry_flush():
    """
    sentry 이벤트 강제 전송 (서버 종료 시 실행)
    """
    sentry_sdk.flush()
