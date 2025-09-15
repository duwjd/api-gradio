"""auto

Revision ID: ae1eea1b02b6
Revises: 305f3a9c4404
Create Date: 2025-05-21 16:11:23.490391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "ae1eea1b02b6"
down_revision: Union[str, None] = "305f3a9c4404"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "resource_analysis",
        "is_active",
        existing_type=mysql.TINYINT(display_width=1),
        server_default=sa.text("0"),  # 이 줄을 꼭 추가
        existing_nullable=True,
        existing_comment="활성 여부",
        comment="활성화 여부",
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    op.alter_column(
        "resource_analysis",
        "is_active",
        existing_type=mysql.TINYINT(display_width=1),
        server_default=sa.text("1"),  # rollback 시 원래대로
        existing_nullable=True,
        existing_comment="활성화 여부",
        comment="활성 여부",
    )

    # ### end Alembic commands ###
