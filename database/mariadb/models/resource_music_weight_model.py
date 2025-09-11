from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from database.mariadb.models import Base, TimestampModel


class ResourceMusicWeight(Base, TimestampModel):
    __tablename__ = "resource_music_weight"

    music_id = Column(INTEGER(display_width=11), primary_key=True, comment="음악 id")
    keyword_id = Column(
        INTEGER(display_width=11),
        ForeignKey("resource_music_keyword.keyword_id"),
        primary_key=True,
        nullable=False,
        comment="키워드 id",
    )
    music_keyword = relationship("ResourceMusicKeyword", back_populates="music_weight")

    weight = Column(
        Float,
        nullable=True,
        comment="가중치",
    )
