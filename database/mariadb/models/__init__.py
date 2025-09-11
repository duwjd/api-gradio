import importlib
import logging
import os
import pkgutil
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    모든 모델이 상속받는 기본 Base 클래스
    """

    pass


class TimestampModel:
    """
    create_at, update_at, delete_at 칼럼 생성 클래스
    """

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)


class Models:
    _models_imported = False  # 중복 실행 방지

    @classmethod
    def models_import(cls):
        """
        models 디렉터리에서 모든 모델을 자동 Import
        """
        logger = logging.getLogger("app")

        if cls._models_imported:
            return  # 이미 Import 되었으면 실행하지 않음

        models_package = __name__  # 현재 패키지 (`database.mariadb.models`)
        models_dir = os.path.dirname(__file__)  # 현재 디렉토리 (`models` 폴더)

        for _, module_name, _ in pkgutil.iter_modules([models_dir]):
            if module_name != "__init__":
                importlib.import_module(f"{models_package}.{module_name}")
                logger.info(f"Import 모델: {models_package}.{module_name}")
