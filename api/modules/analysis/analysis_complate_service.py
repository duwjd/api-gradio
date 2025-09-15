import json
import logging

from api.exceptions import APIException, response_error
from api.modules.analysis.dao.analysis_sqs_queue_dao import (
    get_analysis_producer_sqs_queue,
)
from api.modules.analysis.dao.analysis_task_gradio_dao import (
    get_task_gradio_error_message,
    get_task_gradio_request_body,
    update_task_gradio_error,
    update_task_gradio_init_error,
    update_task_gradio_progress,
    update_task_gradio_result,
    update_task_gradio_status,
)
from api.modules.analysis.processor_complate_filter import processor_complate_filter
from api.modules.analysis.schema.analysis_schema import (
    ReqDoAnalysis,
    ResAnalysisSQSConsumer,
    ResGetAnalysis,
)
from api.modules_master.consumer.schema.consumer_analysis_schema import (
    ReqConsumerAnalysis,
)
from config.const import ANALYSIS_ERROR, S3, STATUS, BaseErrorEnum
from database.mariadb.mariadb_config import AsyncSessionLocal
from utils.s3_util_engine import (
    get_private_s3_key_to_https,
    get_s3_bucket,
    upload_s3_binary,
)
from utils.sqs_util import send_sqs_message

logger = logging.getLogger("app")


class AnalysisComplateService:
    @staticmethod
    async def analysis_complate(req_body: ReqConsumerAnalysis):
        """
        분석 완료 처리
        """
        try:
            # 분석 조회 sqs큐
            analysis_producer_sqs_queue = await get_analysis_producer_sqs_queue()

            async with AsyncSessionLocal() as db:
                status = req_body.status
                error_code = req_body.errorCode
                error_message = req_body.errorMessage

                if status == STATUS.FAIL:
                    raise APIException(ANALYSIS_ERROR[error_code], error_message)

                if status == STATUS.SUCCESS:
                    # 분석 완료 분기
                    result = await processor_complate_filter(req_body, db)
                    result = json.dumps(result, ensure_ascii=False)

                    logger.info(f"분석 결과 : {result}")

                    # 상태 업데이트 (완료)
                    await update_task_gradio_result(req_body, result, db)
                    await update_task_gradio_progress(req_body, 100, db)
                    await update_task_gradio_status(req_body, STATUS.SUCCESS, db)
                    await update_task_gradio_init_error(req_body, db)

                    logger.info(
                        f"userId: {req_body.userId}, projectId: {req_body.projectId}, analysisCode: {req_body.analysisCode}, 분석 결과 : {result}"
                    )

                    # task_gradio request_body 조회
                    task_gradio_request_body = await get_task_gradio_request_body(
                        req_body, db
                    )

                    # S3 업로드
                    await upload_analysis_result(
                        task_gradio_request_body=task_gradio_request_body, result=result
                    )

                    analysis_result_https = (
                        task_gradio_request_body.analysisHttps + S3.ANALYSIS_RESULT
                    )
                    # 분석 조회 SQS queue 성공 메세지 전송
                    await send_sqs_message(
                        queue_url=analysis_producer_sqs_queue,
                        message=ResAnalysisSQSConsumer(
                            httpStatusCode=200,
                            userId=req_body.userId,
                            projectId=req_body.projectId,
                            type=req_body.analysisCode,
                            status=STATUS.SUCCESS,
                            progress=100,
                            result=analysis_result_https,
                            documentS3=task_gradio_request_body.documentS3,
                        ).model_dump_json(exclude_none=True),
                    )
        except Exception as e:
            logger.error(f"분석 완료 중 에러: {e}", exc_info=True)

            error_enum = ANALYSIS_ERROR.AI_API_ANALYSIS_FAIL
            error_detail = None
            error_status_code = 500

            arg = e.args[0] if e.args else None

            if isinstance(arg, BaseErrorEnum):
                error_enum = arg
                if len(e.args) > 1:
                    error_detail = e.args[1]
            elif isinstance(arg, Exception):
                error_detail = str(arg)

            error_code = error_enum.code
            if error_detail == None:
                error_detail = error_enum.message

            error_status_code = error_enum.status_code
            await update_task_gradio_status(req_body, STATUS.FAIL, db)
            await update_task_gradio_error(req_body, error_code, error_detail, db)

            response = response_error(
                error_enum,
                ResGetAnalysis,
                await get_task_gradio_error_message(
                    user_id=req_body.userId,
                    project_id=req_body.projectId,
                    analysis_code=req_body.analysisCode,
                    db=db,
                ),
            )

            # 분석 조회 SQS queue 실패 메세지 전송
            await send_sqs_message(
                queue_url=analysis_producer_sqs_queue,
                message=ResAnalysisSQSConsumer(
                    httpStatusCode=error_status_code,
                    userId=req_body.userId,
                    projectId=req_body.projectId,
                    type=req_body.analysisCode,
                    status=STATUS.FAIL,
                    code=error_code,
                    message=error_detail,
                ).model_dump_json(exclude_none=True),
            )

            return response


async def upload_analysis_result(task_gradio_request_body: ReqDoAnalysis, result: str):
    """
    분석 결과 S3 저장

    Args:
        task_gradio_request_body (ReqDoAnalysis): req_body
        result (str): 분석 결과

    """

    bucket = get_s3_bucket(task_gradio_request_body.analysisS3)
    s3_key = (task_gradio_request_body.analysisS3 + S3.ANALYSIS_RESULT).split(
        bucket + "/"
    )[1]
    json_bytes = result.encode("utf-8")

    # s3 바이너리 업로드
    await upload_s3_binary(
        bucket=bucket,
        s3_key=s3_key,
        binary=json_bytes,
        mime_type="application/json",
    )
