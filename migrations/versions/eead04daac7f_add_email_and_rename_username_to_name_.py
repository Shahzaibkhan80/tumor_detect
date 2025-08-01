"""Add email and rename username to name in Doctor

Revision ID: eead04daac7f
Revises: ec840b6080c7
Create Date: 2025-05-30 01:33:24.109202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eead04daac7f'
down_revision = 'ec840b6080c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('doctor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('doctor', schema=None) as batch_op:
        batch_op.drop_column('email')

    # ### end Alembic commands ###
