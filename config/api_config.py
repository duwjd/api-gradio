"""API 설정 관리"""
import os

class APIConfig:
    # 환경 변수에서 API 서버 주소 가져오기 (기본값 설정)
    API_BASE_URL = os.getenv("API_BASE_URL", "http://192.168.0.146:5005")
    
    # API 엔드포인트
    ANALYSIS_ENDPOINT = "/api/analysis/document"
    ANALYSIS_STATUS_ENDPOINT = "/api/analysis/document/{user_id}/{project_id}"
    
    REQUEST_TIMEOUT = 30.0
    CONNECT_TIMEOUT = 10.0
    
    # 재시도 설정
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    @classmethod
    def get_analysis_url(cls):
        """분석 요청 URL 반환"""
        return f"{cls.API_BASE_URL}{cls.ANALYSIS_ENDPOINT}"
    
    @classmethod
    def get_status_url(cls, user_id: int, project_id: int):
        """분석 상태 조회 URL 반환"""
        endpoint = cls.ANALYSIS_STATUS_ENDPOINT.format(
            user_id=user_id,
            project_id=project_id
        )
        return f"{cls.API_BASE_URL}{endpoint}"