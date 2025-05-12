from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = '001_seed_galactic_object_types'
down_revision = 'f2ac6da94ee5'
branch_labels = None
depends_on = None

def upgrade():
    seed_data = [
        {"uuid": str(uuid.uuid4()), "name": "Star"},
        {"uuid": str(uuid.uuid4()), "name": "Planet"},
        {"uuid": str(uuid.uuid4()), "name": "Asteroid"},
        {"uuid": str(uuid.uuid4()), "name": "Comet"},
        {"uuid": str(uuid.uuid4()), "name": "Nebula"},
    ]

    for data in seed_data:
        op.execute(
            f"INSERT INTO galactic_object_types (uuid, name) VALUES ('{data['uuid']}', '{data['name']}')"
        )

def downgrade():
    op.execute("DELETE FROM galactic_object_types")