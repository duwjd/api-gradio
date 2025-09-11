from sqlalchemy import select
from sqlalchemy.orm import Session

from database.mariadb.models.resource_vessl_model import ResourceVessl


def get_vessl(db: Session):
    """
    vessl-host, port 조회
    """
    query = select(ResourceVessl)
    result = db.execute(query)
    row = result.scalars().first()

    host = row.host
    port = row.port

    return host, port
