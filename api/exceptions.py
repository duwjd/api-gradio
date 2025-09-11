import json
import logging
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config.const import ANALYSIS_ERROR, STATUS, BaseErrorEnum

logger = logging.getLogger("app")


class ResError(BaseModel):
    status: STATUS
    code: Optional[str] = None
    message: Optional[str] = None


async def validation_exception_handler(request: Request, error: RequestValidationError):
    """
    422 (ValidationError) 예외 처리
    """
    try:
        body = await request.json()
        logger.error(f"param: {json.dumps(body, ensure_ascii=False)}")
    except Exception:
        body = None

    logger.error(f"{str(error)}", exc_info=True)
    return JSONResponse(
        status_code=422,
        content={"status": "fail", "message": str(error)},
    )


async def exception_handler(request: Request, error: Exception):
    """
    에러 예외 처리 핸들러 - 모든 예외 처리 가능
    """

    status_code = 500
    error_message = str(error)

    # HTTPException (400, 404, 403 등) 처리
    if isinstance(error, HTTPException):
        status_code = error.status_code
        error_message = error.detail

    logger.error(f"{str(error)}", exc_info=True)
    return JSONResponse(
        status_code=status_code,
        content={"status": "fail", "message": error_message},
    )


def response_error(error_code: ANALYSIS_ERROR, schema: any, error_detail: str = None):
    """
    에러 코드 반환 함수

    Args:
        error_code (ANALYSIS_ERROR): 에러 코드
        schema (any): 모델
    """

    content = schema(
        status=STATUS.FAIL,
        code=error_code.code,
        message=error_code.message,
    ).dict(exclude_none=True)

    if error_detail != None:
        content["message"] = error_detail

    logger.error(f"[에러 응답 JSON] {json.dumps(content, ensure_ascii=False)}")

    return JSONResponse(
        status_code=error_code.status_code,
        content=content,
    )
