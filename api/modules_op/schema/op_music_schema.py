from typing import Optional

from fastapi import UploadFile

from api.modules.schema import BaseConfigModel


class ReqCreateBgm:
    def __init__(
        self,
        license: Optional[str],
        name: Optional[str],
        duration: Optional[int],
        mood: Optional[str],
        file: UploadFile,
    ):
        self.license = license
        self.name = name
        self.duration = duration
        self.mood = mood
        self.file = file

    def as_dict(self):
        return {
            "license": self.license,
            "name": self.name,
            "duration": self.duration,
            "mood": self.mood,
            "filename": self.file.filename if self.file else None,
            "content_type": self.file.content_type if self.file else None,
        }


class ResGetBgm(BaseConfigModel):
    music_id: int
    license: str
    name: str
    url: str
    mood: str
    duration: int
    created_at: Optional[str]
    updated_at: Optional[str]


class ReqUpdateBgm(BaseConfigModel):
    license: Optional[str]
    name: Optional[str]
    duration: Optional[int]


class ReqDeleteBgm(BaseConfigModel):
    music_id: int
