from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def version_doc():
    return {
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "version": "version 정보",
                    }
                }
            },
        },
    }


def helath_check_doc():
    return {
        200: {
            "content": {"application/json": {"example": {"status": "ok"}}},
        },
    }


def remove_422_doc(app: FastAPI):
    """Swagger 문서에서 422 응답을 제거하는 함수"""

    # 이미 변경된 스키마가 있으면 기존 것을 반환하여 중복 실행 방지
    if app.openapi_schema:
        return app.openapi_schema

    # 원래 OpenAPI 스키마 가져오기
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 422 응답 제거
    for path, methods in openapi_schema["paths"].items():
        for method in methods:
            if "responses" in methods[method]:
                methods[method]["responses"].pop("422", None)

    # 수정된 OpenAPI 스키마를 저장하여 중복 실행 방지
    app.openapi_schema = openapi_schema
    return app.openapi_schema
