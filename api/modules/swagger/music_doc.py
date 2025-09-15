def get_bgms_doc():
    """음악 목록 API swagger doc"""
    return {
        200: {
            "content": {
                "application/json": {
                    "example": [
                        {
                            "musicId": 4,
                            "name": "Ai - 7080 Sound",
                            "bgmUrl": "https://cat-10k1m.s3.ap-northeast-2.amazonaws.com/library/sound/music/music_1.mp3",
                        }
                    ]
                }
            },
        },
        500: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "fail",
                        "message": "에러 메세지",
                        "code": "에러 코드",
                    }
                }
            },
        },
    }


def do_random_bgm_doc():
    """랜덤 음악 API swagger doc"""
    return {
        500: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "fail",
                        "message": "에러 메세지",
                        "code": "에러 코드",
                    }
                }
            },
        },
    }
