from sqlalchemy import Column, String, Text

from database.mariadb.models import Base, TimestampModel


class ResourceVessl(Base, TimestampModel):
    __tablename__ = "resource_vessl"
    name = Column(
        String(255),
        primary_key=True,
        comment="vessl 서버 이름",
    )
    host = Column(String(255), nullable=True, comment="서버 ip")
    port = Column(String(255), nullable=True, comment="서버 port")
