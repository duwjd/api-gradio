import os
from dotenv import load_dotenv, find_dotenv


def load_environment():
    """
    ENV 환경 변수에 따라 적절한 .env 파일을 로드
    """

    env = os.getenv("ENV")
    env_file = f"env/.{env}.env"  # 예: 'env/.development.env'
    env_path = find_dotenv(env_file)

    if env_path:
        load_dotenv(env_path)
    else:
        raise FileNotFoundError(f"Environment file {env_file} not found.")
