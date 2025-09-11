from api.modules.analysis.schema.analysis_schema import ResDoAnalysis


def do_analysis_doc():
    """분석 요청 API swagger doc"""
    return {
        201: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "문서 분석이 백그라운드에서 실행됩니다.",
                        "documentS3": [],
                    }
                }
            },
        },
        400: {
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


def get_analysis_doc():
    """분석 조회 API swagger doc"""
    return {
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "progress | success",
                        "progress": "0~100 (int)",
                    }
                }
            },
        },
        400: {
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
