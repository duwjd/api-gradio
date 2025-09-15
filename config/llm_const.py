class LLM:
    GPT_O_4_MINI = "o4-mini-2025-04-16"
    GPT_4_O = "gpt-4o"
    GPT_4_1 = "gpt-4.1"
    GPT_IMAGE_1 = "gpt-image-1"
    GEMINI_FLASH = "gemini-2.0-flash"
    GEMINI_PRO = "gemini-1.5-pro"
    GEMINI_2_5_FLASH = "gemini-2.5-flash-preview-05-20"
    GEMINI_2_5_PRO = "gemini-2.5-pro-preview-06-05"
    GPT_5 = "gpt-5"
    GPT_5_NANO = "gpt-5-nano"


class LLM_CODE:
    CHATGPT = "LLM-CHATGPT"
    GEMINI = "LLM-GEMINI"


class LLMConfig:
    MAX_OUTPUT_TOKENS = 10000
    TIMEOUT = 30


class GPTParams:
    TEMPERATURE = 0.01
    TOP_P = 0.9


class GEMINIParams:
    TEMPERATURE = 0.01
    TOP_P = 0.9


class GEMINISafetyCategory:
    """
    Gemini Safety Category
    """

    HARASSMENT = "HARM_CATEGORY_HARASSMENT"  # 괴롭힘콘텐츠
    HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"  # 증오심표현및콘텐츠
    SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"  # 성적으로노골적인콘텐츠
    DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"  # 위험한콘텐츠
    CIVIC_INTEGRITY = (
        "HARM_CATEGORY_CIVIC_INTEGRITY"  # 시민의품위를해치는데사용될수있는콘텐츠
    )


class GEMINISafetyThreshold:
    """
    Gemini Safety Threshold
    """

    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"
    # NEGLIGIBLE이 포함된 콘텐츠는 허용됩니다.

    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    # NEGLIGIBLE(무시할만함) 및 LOW(낮음)인 콘텐츠는 허용됩니다.

    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    # NEGLIGIBLE(무시할만한수준), LOW(낮음), MEDIUM(중간)인콘텐츠는 허용됩니다.

    BLOCK_NONE = "BLOCK_NONE"
    # 모든 콘텐츠가 허용됩니다.

    OFF = "OFF"
    # 안전 필터를 사용 중지합니다.
