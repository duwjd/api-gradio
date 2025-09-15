from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from api.modules_op.schema.op_music_schema import ReqCreateBgm, ResGetBgm
from database.mariadb.models.resource_music_model import ResourceMusic


async def op_is_music_id(music_id: int, db: Session):
    """
    op bgm id 확인
    """
    query = select(ResourceMusic).where(
        ResourceMusic.music_id == music_id, ResourceMusic.deleted_at.is_(None)
    )

    result = await db.execute(query)
    analysis = result.scalars().first()

    if analysis:
        return True
    return False


async def op_create_bgm(req_body: ReqCreateBgm, db: Session):
    """
    op bgm 생성
    """
    req_body.pop("filename")
    req_body.pop("content_type")

    query = insert(ResourceMusic).values(req_body)

    await db.execute(query)
    await db.commit()


async def op_get_bgms(db: Session):
    """
    op bgm 조회
    """
    query = select(
        ResourceMusic.music_id,
        ResourceMusic.license,
        ResourceMusic.name,
        ResourceMusic.url,
        ResourceMusic.mood,
        ResourceMusic.duration,
        getattr(ResourceMusic, "created_at"),
        getattr(ResourceMusic, "updated_at"),
    ).where(ResourceMusic.deleted_at.is_(None))

    result = await db.execute(query)
    rows = result.mappings().all()

    # 리스트 딕셔너리 형태로 가공
    response_data = [
        ResGetBgm(
            music_id=row["music_id"],
            license=row["license"],
            name=row["name"],
            url=row["url"],
            mood=row["mood"],
            duration=row["duration"],
            created_at=row["created_at"].isoformat() if row["created_at"] else None,
            updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
        ).model_dump()
        for row in rows
    ]

    return response_data


async def op_update_bgm():
    """
    op bgm 수정
    """
    pass


async def op_delete_bgm(music_id: int, db: Session):
    """
    op bgm 삭제
    """
    query = (
        update(ResourceMusic)
        .where(ResourceMusic.music_id == music_id)
        .values(deleted_at=datetime.utcnow())
    )

    await db.execute(query)
    await db.commit()
