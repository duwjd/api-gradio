# scripts 샘플
#     "scripts": [
#         {
#             "image_number": "image1",
#             "title": "칠흑과 눈의 향기",
#             "tag_line": "겨울 속 전통의 표지",
#             "caption": "고요한 겨울 풍경에 자리한 전통의 표지판, 시간의 이야기를 들려줍니다.",
#         },
#         {
#             "image_number": "image2",
#             "title": "신성의 문턱",
#             "tag_line": "겨울의 신비로운 입구",
#             "caption": "신비로운 토리이 게이트가 신성함으로 초대합니다.",
#         },
#         {
#             "image_number": "image3",
#             "title": "역사의 빛",
#             "tag_line": "고전 랜턴의 겨울 낭만",
#             "caption": "고전적 아름다움과 역사의 매력이 살아있는 돌 랜턴이 기다립니다.",
#         },
#         {
#             "image_number": "image4",
#             "title": "숲의 겨울 여행",
#             "tag_line": "함께 하는 설원의 산책",
#             "caption": "눈길을 따라 걷는 이들, 숲의 고요함에 생기를 더합니다.",
#         },
#     ]


async def result_json(texts: list[dict], video_urls: list[str]) -> dict:
    result = {}

    result = await text_json(result, texts)
    result = await video_json(result, video_urls)
    result["audios"] = []

    return result


async def text_json(result: dict, texts: dict) -> dict:
    """
    photo2video scene to json 생성
    """
    result["scenes"] = []
    scripts = texts["results"]

    for i, script in enumerate(scripts):
        start = i * 5000
        end = start + 5000

        json = {
            "timeFrame": {"start": start, "end": end},
            "elements": [
                {
                    "type": "text",
                    "category": "title",
                    "text": script.get("title", ""),
                    "timeFrame": {"start": start, "end": end},
                },
                {
                    "type": "text",
                    "category": "tag-line",
                    "text": script.get("tag_line", ""),
                    "timeFrame": {"start": start, "end": end},
                },
                {
                    "type": "text",
                    "category": "caption",
                    "text": script.get("caption", ""),
                    "timeFrame": {"start": start, "end": end},
                },
            ],
        }

        result["scenes"].append(json)

    return result


async def video_json(result: dict, video_urls: list[str]) -> dict:
    """
    photo2video global to json 생성
    """
    result["globals"] = []

    for i, url in enumerate(video_urls):
        start = i * 5000
        end = start + 5000

        json = {
            "type": "video",
            "src": url,
            "duration": 5000,
            "timeFrame": {"start": start, "end": end},
        }

        result["globals"].append(json)

    return result
