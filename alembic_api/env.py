import os

from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, pool

from config.env_config import load_environment
from database.mariadb.models.api_models import ApiModels

config = context.config


def get_db_url():
    """
    환경 변수에서 DB 정보를 가져와 SQLAlchemy URL 생성
    """
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DATABASE = os.getenv("DB_DATABASE")

    return (
        f"mariadb+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )


def run_migrations_online():
    load_environment()

    target_metadata = ApiModels.get_metadata()
    script = ScriptDirectory.from_config(config)

    connectable = create_engine(get_db_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            script=script,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
