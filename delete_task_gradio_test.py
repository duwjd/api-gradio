"""
TaskGradio 테이블의 모든 데이터를 삭제하는 스크립트 :::: 테스트용도로 쓰는 임시 파일
주의: 이 작업은 되돌릴 수 없습니다.
"""
import os
import sys

# 환경 변수 설정 (데이터베이스 config 로드 전에 먼저 설정)
os.environ['ENV'] = 'local'  # 또는 'dev', 'stg', 'prd' 등 사용하고자 하는 환경

from sqlalchemy import delete, func, select
from database.mariadb.mariadb_config import SessionLocal
from database.mariadb.models.task_gradio_model import TaskGradio

def get_record_count():
    """현재 TaskGradio 테이블의 레코드 수를 조회"""
    with SessionLocal() as db:
        query = select(func.count()).select_from(TaskGradio)
        result = db.execute(query)
        return result.scalar()


def clear_task_gradio_table():
    """TaskGradio 테이블의 모든 데이터를 삭제"""
    try:
        with SessionLocal() as db:
            # 현재 레코드 수 확인
            current_count = get_record_count()
            print(f"현재 TaskGradio 테이블에 {current_count}개의 레코드가 있습니다.")
            
            if current_count == 0:
                print("삭제할 데이터가 없습니다.")
                return
            
            # 사용자 확인
            confirm = input(f"\n정말로 모든 {current_count}개의 레코드를 삭제하시겠습니까? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("작업이 취소되었습니다.")
                return
            
            # 재확인
            final_confirm = input("이 작업은 되돌릴 수 없습니다. 정말 진행하시겠습니까? (DELETE): ")
            
            if final_confirm != 'DELETE':
                print("작업이 취소되었습니다.")
                return
            
            # 모든 레코드 삭제
            delete_query = delete(TaskGradio)
            result = db.execute(delete_query)
            deleted_count = result.rowcount
            
            # 트랜잭션 커밋
            db.commit()
            
            print(f"성공적으로 {deleted_count}개의 레코드가 삭제되었습니다.")
            
            # 삭제 후 레코드 수 확인
            remaining_count = get_record_count()
            print(f"현재 TaskGradio 테이블에 {remaining_count}개의 레코드가 남아있습니다.")
            
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("TaskGradio 테이블 데이터 삭제 스크립트")
    print("=" * 50)
    
    try:
        success = clear_task_gradio_table()
        if success:
            print("\n스크립트가 성공적으로 완료되었습니다.")
        else:
            print("\n스크립트 실행 중 오류가 발생했습니다.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)