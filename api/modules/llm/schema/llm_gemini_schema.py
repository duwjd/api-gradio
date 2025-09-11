from google.genai import types
from typing import Final

class GeminiPhoto2VideoOutput:
    SCHEMA: Final[types.Schema] = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "image_number": types.Schema(type=types.Type.INTEGER),
            "title": types.Schema(type=types.Type.STRING),
            "tag_line": types.Schema(type=types.Type.STRING),
            "caption": types.Schema(type=types.Type.STRING),
            "video_prompt": types.Schema(type=types.Type.STRING),
        },
        required=["image_number", "title", "tag_line", "caption", "video_prompt"],
    )

class GeminiPhoto2VideoOutputs:
    SCHEMA: Final[types.Schema] = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "results": types.Schema(
                type=types.Type.ARRAY,
                items=GeminiPhoto2VideoOutput.SCHEMA,
            ),
        },
        required=["results"],
    )

class GeminiContext2Video:
    SCHEMA: Final[types.Schema] = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "video_prompt": types.Schema(type=types.Type.STRING),
        },
        required=["video_prompt"],
    )

class GeminiGps2KeywordList:
    SCHEMA: Final[types.Schema] = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "keywords": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["keywords"],
    )