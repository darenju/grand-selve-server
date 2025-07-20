"""create ignore_accents collate

Revision ID: 20e3fde0df58
Revises: 490711c3f64d
Create Date: 2025-07-20 22:31:37.227543

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20e3fde0df58'
down_revision = '490711c3f64d'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE COLLATION IF NOT EXISTS ignore_accents (
            provider = icu,
            locale = 'fr-u-ks-level1',
            deterministic = false
        );
    """)

def downgrade():
    op.execute("DROP COLLATION IF EXISTS ignore_accents;")
