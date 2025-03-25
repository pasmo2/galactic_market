from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from models import GalacticObjectType, db

revision = '001_seed_galactic_object_types'
down_revision = 'f2ac6da94ee5'
branch_labels = None
depends_on = None

def upgrade():
    seed_data = [
        {"name": "Star"},
        {"name": "Planet"},
        {"name": "Asteroid"},
        {"name": "Comet"},
        {"name": "Nebula"},
    ]

    galactic_object_types = [
        GalacticObjectType(name=data["name"]) for data in seed_data
    ]

    db.session.bulk_save_objects(galactic_object_types)
    db.session.commit()

def downgrade():
    GalacticObjectType.query.delete()
    db.session.commit()