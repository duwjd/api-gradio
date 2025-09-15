import os

from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, pool

from config.env_config import load_environment
from database.mariadb.models.op_models import OpModels

config = context.config


def get_op_db_url():
    """
    환경 변수에서 DB 정보를 가져와 SQLAlchemy URL 생성
    """
    DB_HOST_OP = os.getenv("DB_HOST_OP")
    DB_PORT_OP = os.getenv("DB_PORT_OP", "3306")
    DB_USER_OP = os.getenv("DB_USER_OP")
    DB_PASSWORD_OP = os.getenv("DB_PASSWORD_OP")
    DB_DATABASE_OP = os.getenv("DB_DATABASE_OP")

    return f"mariadb+pymysql://{DB_USER_OP}:{DB_PASSWORD_OP}@{DB_HOST_OP}:{DB_PORT_OP}/{DB_DATABASE_OP}"


def run_migrations_online():
    load_environment()

    target_metadata = OpModels.get_metadata()
    script = ScriptDirectory.from_config(config)

    connectable = create_engine(get_op_db_url(), poolclass=pool.NullPool)

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
