import sqlalchemy as sa
from alembic import op

revision: str = '57a48c210abc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'buildings',
        sa.Column('building_id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('address', sa.String(length=1024), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
    )

    op.create_table(
        'activity_types',
        sa.Column('activity_type_id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('activity_types.activity_type_id', ondelete='SET NULL'),
                  nullable=True),
    )

    op.create_table(
        'organizations',
        sa.Column('organization_id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('building_id', sa.Integer(), sa.ForeignKey('buildings.building_id', ondelete='CASCADE'),
                  nullable=False),
    )

    op.create_table(
        'phones',
        sa.Column('phone_id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('number', sa.String(length=50), nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.organization_id', ondelete='CASCADE'),
                  nullable=False),
    )

    op.create_table(
        'organization_activity',
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.organization_id', ondelete='CASCADE'),
                  primary_key=True, nullable=False),
        sa.Column('activity_type_id', sa.Integer(),
                  sa.ForeignKey('activity_types.activity_type_id', ondelete='CASCADE'),
                  primary_key=True, nullable=False),
    )


def downgrade():
    op.drop_table('organization_activity')
    op.drop_table('phones')
    op.drop_table('organizations')
    op.drop_table('activity_types')
    op.drop_table('buildings')
