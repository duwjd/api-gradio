# import json
# import logging
# from typing import List

# from fastapi import Response

# from api.modules.analysis.dao.analysis_task_llm_dao import update_task_llm_status
# from api.modules.analysis.schema.analysis_schema import ReqDoAnalysis, ResGetAnalysis
# from api.modules.engine.dao.engine_task_engine_dao import (
#     init_task_engine,
#     is_group_status_task_engine,
#     update_task_engine,
# )
# from api.modules.engine.dao.engine_task_llm_dao import update_engine_task_llm_status
# from api.modules.engine.schema.aws_schema import (
#     ReqDownloadS3PresignedUrl,
#     ReqUploadS3PresignedUrl,
#     ResDownloadS3PresignedUrl,
#     ResUploadS3PresignedUrl,
# )
# from api.modules.engine.schema.engine_schema import (
#     ReqInitTaskEngine,
#     ReqUpdateTaskEngineStatus,
#     ReqUpdateTaskLLMStatus,
#     ResUpdateTaskEngineStatus,
# )
# from api.modules.llm.llm_chatgpt import chatgpt_analysis_engine
# from api.modules.llm.llm_gemini import gemini_analysis_engine
# from api.modules.llm.schema.llm_schema import ReqDoLLM, ResGetLLM
# from config.const import ANALYSIS_ERROR, STATUS
# from database.mariadb.mariadb_config import (
#     AsyncSessionDev,
#     AsyncSessionLocal,
#     AsyncSessionPrd,
#     AsyncSessionStg,
# )
# from utils.s3_util_engine import download_s3_presigned_url, upload_s3_presigned_url

# logger = logging.getLogger("app")


# class EngineService:
#     @staticmethod
#     async def upload_s3_presigned_url(req_body: List[ReqUploadS3PresignedUrl]):
#         """
#         s3 업로드 presigned url  생성
#         """
#         result: List[ResUploadS3PresignedUrl] = []

#         for body in req_body:
#             # S3 업로드 presigned-url 생성
#             presigend_url = await upload_s3_presigned_url(body)
#             result.append(presigend_url)

#         return result

#     @staticmethod
#     async def download_s3_presigned_url(req_body: ReqDownloadS3PresignedUrl):
#         """
#         s3 다운로드 presigned url 생성
#         """
#         # s3 presigned url 리턴
#         return ResDownloadS3PresignedUrl(
#             presignedUrl=await download_s3_presigned_url(req_body)
#         )

#     @staticmethod
#     async def do_llm_gemini(req_body: ReqDoLLM):
#         """
#         llm gemini 요청
#         """

#         async with AsyncSessionLocal() as db:
#             return ResGetLLM(result=await gemini_analysis_engine(req_body, db))

#     @staticmethod
#     async def do_llm_chatgpt(req_body: ReqDoLLM):
#         """
#         llm chatgpt 요청
#         """

#         try:
#             async with AsyncSessionLocal() as db:
#                 return ResGetLLM(result=await chatgpt_analysis_engine(req_body, db))
#         except Exception as e:
#             logger.error(f"llm chatgpt 요청 에러: {e}", exc_info=True)
#             raise e

#     @staticmethod
#     async def get_s3_presigned_url_https(s3_keys: list[str]):
#         """
#         s3 https url 조회
#         """
#         result_s3_presigned_url: list[str] = []
#         result_s3_https_url: list[str] = []
#         for s3_key in s3_keys:
#             presignedUrl = await download_s3_presigned_url(
#                 ReqDownloadS3PresignedUrl(s3Path=s3_key), expires_in=6000
#             )

#             https_url = presignedUrl.split("?X-Amz-Algorithm")[0]
#             result_s3_presigned_url.append(presignedUrl)
#             result_s3_https_url.append(https_url)

#         return result_s3_presigned_url, result_s3_https_url

#     @staticmethod
#     async def update_engine_task_llm_status(req_body: ReqUpdateTaskLLMStatus):
#         """
#         engine 서버 호출용 task_llm 상태 수정
#         """
#         try:
#             logger.info(
#                 f"task_llm 상태 수정 params: {json.dumps(req_body.dict(), ensure_ascii=False)}"
#             )
#             env = req_body.env
#             env_session_map = {
#                 "local": AsyncSessionLocal,
#                 "development": AsyncSessionDev,
#                 "staging": AsyncSessionStg,
#                 "product": AsyncSessionPrd,
#             }

#             if env not in env_session_map:
#                 raise Exception(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis)

#             async with AsyncSessionLocal() as db:
#                 await update_engine_task_llm_status(req_body, db)
#                 return Response(status_code=200)
#         except Exception as e:
#             logger.error(f"task 상태 수정 에러: {e}", exc_info=True)
#             raise e

#     @staticmethod
#     async def init_task_engine(req_body: ReqInitTaskEngine):
#         """
#         engine 서버 호출용 task_engine 수정
#         """
#         try:
#             logger.info(
#                 f"task_engine 초기화 params: {json.dumps(req_body.dict(), ensure_ascii=False)}"
#             )

#             env = req_body.env
#             env_session_map = {
#                 "local": AsyncSessionLocal,
#                 "development": AsyncSessionDev,
#                 "staging": AsyncSessionStg,
#                 "product": AsyncSessionPrd,
#             }

#             if env not in env_session_map:
#                 raise Exception(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis)

#             async with AsyncSessionLocal() as db:
#                 await init_task_engine(req_body, db)
#                 await update_task_llm_status(
#                     ReqDoAnalysis(
#                         userId=req_body.user_id,
#                         projectId=req_body.project_id,
#                         type=req_body.analysis_code,
#                     ),
#                     STATUS.PROGRESS,
#                     db,
#                 )

#                 return Response(status_code=200)
#         except Exception as e:
#             logger.error(f"task 상태 수정 에러: {e}", exc_info=True)
#             raise e

#     @staticmethod
#     async def update_task_engine(req_body: ReqUpdateTaskEngineStatus):
#         """
#         engine 서버 호출용 task_engine 수정
#         """
#         try:
#             logger.info(
#                 f"task_engine 상태 수정 params: {json.dumps(req_body.dict(), ensure_ascii=False)}"
#             )
#             env = req_body.env
#             env_session_map = {
#                 "local": AsyncSessionLocal,
#                 "development": AsyncSessionDev,
#                 "staging": AsyncSessionStg,
#                 "product": AsyncSessionPrd,
#             }

#             if env not in env_session_map:
#                 raise Exception(ANALYSIS_ERROR.AI_API_ENV_NOT_EXIST, ResGetAnalysis)

#             async with AsyncSessionLocal() as db:
#                 # group 상태 반환
#                 group_status = await is_group_status_task_engine(req_body, db)
#                 if group_status == False:
#                     # task_engine 상태 실패로 변경
#                     req_body.status = STATUS.FAIL

#                 # task_engine 상태 수정
#                 await update_task_engine(req_body, db)

#                 return ResUpdateTaskEngineStatus(group_status=group_status)

#         except Exception as e:
#             logger.error(f"task 상태 수정 에러: {e}", exc_info=True)
#             raise e
