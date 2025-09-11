from enum import Enum
from typing import Any, List, Optional, Union, Final

from pydantic import Field

from api.modules.schema import BaseConfigModel
from config.const import BaseStrEnum

class Section(BaseConfigModel):
    text_main: str = Field(alias="text-main")
    text_extra: List[str] = Field(alias="text-extra")
    image: str


class Scene(BaseConfigModel):
    script: str
    title_main: str = Field(alias="title-main")
    title_extra: List[str] = Field(alias="title-extra")
    images: List[str]
    sections: List[Section]


class LLMOutput(BaseConfigModel):
    scene: Scene


class PositionRatio(BaseConfigModel):
    x: float
    y: float


class SectionRatio(BaseConfigModel):
    text_main: str = Field(alias="text-main")
    position_ratio: PositionRatio
    font_size_ratio: float = Field(alias="font-size-ratio")
    font_color: str = Field(alias="font-color")
    bold: bool
    italic: bool


class ObjectInfo(BaseConfigModel):
    year: str
    name: str
    color: str


class SceneRatio(BaseConfigModel):
    sections: List[SectionRatio]
    object: List[ObjectInfo]


class GPTOutput(BaseConfigModel):
    scenes: List[LLMOutput]


class GPTOutput_OCR_Ratio(BaseConfigModel):
    scene: SceneRatio


class GPTOutput_Prompt(BaseConfigModel):
    prompt: str


class GPTImage2Context(BaseConfigModel):
    image_number: str
    description: str
    caption: str


class GPTImage2ContextList(BaseConfigModel):
    contexts: List[GPTImage2Context]


class GPTContext2Script(BaseConfigModel):
    image_number: str
    title: str
    tag_line: str
    caption: str


class GPTContext2ScriptList(BaseConfigModel):
    results: List[GPTContext2Script]


class GPTContext2Video(BaseConfigModel):
    video_prompt: str


class GPTContext2VideoList(BaseConfigModel):
    video_prompts: List[GPTContext2Video]


class GPTGps2KeywordList(BaseConfigModel):
    keywords: List[str]


## GPT category based request


class Photo2VideoCategoryChoiceEnum(str, BaseStrEnum):
    travel = "travel"
    food = "food"
    cuteness = "cuteness"
    personal = "personal"
    activity = "activity"


class GPTPhoto2VideoCategoryOutput(BaseConfigModel):
    category: Photo2VideoCategoryChoiceEnum


# # 이미지 1장당 모두 하나씩 뽑을때
class GPTPhoto2VideoOutput(BaseConfigModel):
    image_number: int
    title: str
    tag_line: str
    caption: str
    video_prompt: str


class GPTPhoto2VideoOutputs(BaseConfigModel):
    results: List[GPTPhoto2VideoOutput]


# 이미지 1장당 캡션 하나씩만 뽑을때
# class GPTPhoto2VideoOutput(BaseConfigModel):
#     image_number: int
#     caption: str
#     video_prompt: str

# class GPTPhoto2VideoOutputs(BaseConfigModel):
#     title: str
#     tag_line: str
#     results: List[GPTPhoto2VideoOutput]


class GPTPhoto2MusicOutput(BaseConfigModel):
    music_prompt: str