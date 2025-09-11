from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER

from database.mariadb.models import Base, TimestampModel


class ResourceMusic(Base, TimestampModel):
    __tablename__ = "resource_music"

    music_id = Column(INTEGER(display_width=11), primary_key=True, comment="음악 id")
    license = Column(
        String(255),
        nullable=True,
        comment="음악 라이센스",
    )
    url = Column(
        String(255),
        nullable=True,
        comment="음악 url (ex: https://cat-10k1m.s3.ap-northeast-2.amazonaws.com/library/sound/bgm/brand/BalloonPlanet-Cool_My_Bass.mp3)",
    )
    name = Column(String(255), nullable=True, comment="음악 이름")
    mood = Column(String(255), nullable=True, comment="음악 분위기")
    duration = Column(
        INTEGER(display_width=11), nullable=True, comment="음악 길이 (초)"
    )
