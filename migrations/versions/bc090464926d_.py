"""empty message

Revision ID: bc090464926d
Revises: 75184929ee53
Create Date: 2019-10-17 20:19:38.203503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc090464926d'
down_revision = '75184929ee53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website', sa.String(length=500), nullable=True))
    op.alter_column('Artist', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.add_column('Venue', sa.Column('website', sa.String(length=500), nullable=True))
    op.alter_column('Venue', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.drop_column('Venue', 'website')
    op.alter_column('Artist', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.drop_column('Artist', 'website')
    # ### end Alembic commands ###
