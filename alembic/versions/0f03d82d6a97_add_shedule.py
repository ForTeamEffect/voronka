"""Add shedule

Revision ID: 0f03d82d6a97
Revises: b5cad2a3aca6
Create Date: 2024-02-29 06:28:53.816005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f03d82d6a97'
down_revision: Union[str, None] = 'b5cad2a3aca6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('schedule', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'schedule')
    # ### end Alembic commands ###
