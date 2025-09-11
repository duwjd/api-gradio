from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from database.mariadb.models import Base, TimestampModel


class ResourceMusicKeyword(Base, TimestampModel):
    __tablename__ = "resource_music_keyword"

    keyword_id = Column(
        INTEGER(display_width=11), primary_key=True, comment="키워드 id"
    )
    keyword_ko = Column(String(255), nullable=True, comment="한국어 키워드")
    keyword_en = Column(String(255), nullable=True, comment="영어 키워드")

    music_weight = relationship("ResourceMusicWeight", back_populates="music_keyword")
