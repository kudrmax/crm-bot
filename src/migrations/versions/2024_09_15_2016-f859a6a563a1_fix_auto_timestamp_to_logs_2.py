"""Fix auto timestamp to logs 2

Revision ID: f859a6a563a1
Revises: 00458f8f0914
Create Date: 2024-09-15 20:16:21.285363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f859a6a563a1'
down_revision: Union[str, None] = '00458f8f0914'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
