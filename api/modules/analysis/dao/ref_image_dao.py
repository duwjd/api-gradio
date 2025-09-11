from sqlalchemy import select, text
from sqlalchemy.orm import Session

from database.mariadb.models.resource_ref_image_modle import ResourceRefImage
from utils.s3_util_engine import get_public_https_to_s3_key
from config.const import S3


async def get_ref_images(object: dict, db: Session):
    """
    reference image 조회
    """
    year = object["year"]
    name = object["name"]
    color = object["color"]

    query = (
        select(ResourceRefImage)
        .where(
            text('JSON_UNQUOTE(JSON_EXTRACT(option, "$.year")) = :year'),
            text('JSON_UNQUOTE(JSON_EXTRACT(option, "$.name")) = :name'),
            text('JSON_UNQUOTE(JSON_EXTRACT(option, "$.color")) = :color'),
        )
        .params(year=year, name=name, color=color)
    )

    result = await db.execute(query)
    row = result.scalars().first()

    if not row:
        query = (
            select(ResourceRefImage)
            .where(
                text('JSON_UNQUOTE(JSON_EXTRACT(option, "$.name")) = :name'),
                text('JSON_UNQUOTE(JSON_EXTRACT(option, "$.color")) = :color'),
            )
            .params(name=name, color=color)
        )

        result = await db.execute(query)
        row = result.scalars().first()

        if not row:
            query = (
                select(ResourceRefImage)
                .where(
                    text('JSON_UNQUOTE(JSON_EXTRACT(option, "$.name")) = :name'),
                )
                .params(name=name)
            )

        result = await db.execute(query)
        row = result.scalars().first()

        if not row:
            return None

    ref_image_key = get_public_https_to_s3_key(S3.BUCKET, row.image_url)
    ref_mask_key = get_public_https_to_s3_key(S3.BUCKET, row.mask_url)

    return ref_image_key, ref_mask_key
