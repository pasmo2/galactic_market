from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    permissions = db.Column(db.ARRAY(db.String))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

class GalacticObjectType(db.Model):
    __tablename__ = 'galactic_object_types'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)

class GalacticObject(db.Model):
    __tablename__ = 'galactic_objects'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('galactic_object_types.uuid'))
    mass_kg = db.Column(db.Float, nullable=False)
    radius_km = db.Column(db.Float, nullable=False)
    distance_from_earth_parsec = db.Column(db.Float, nullable=False)
    discovered_at = db.Column(db.TIMESTAMP)
    owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid'))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())

class Certificate(db.Model):
    __tablename__ = 'certificates'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    owner = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid'))
    valid_from = db.Column(db.TIMESTAMP)
    valid_until = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, onupdate=db.func.now())

class Demand(db.Model):
    __tablename__ = 'demands'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.uuid'))
    galactic_object_id = db.Column(UUID(as_uuid=True), db.ForeignKey('galactic_objects.uuid'))
    price_eur = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', name='demand_status'), default='pending')
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())