from flask import jsonify, request, Blueprint, abort
from models import db, User, GalacticObject, GalacticObjectType, Demand
from werkzeug.security import generate_password_hash
from uuid import uuid4


users_bp = Blueprint('users', __name__)
demand_bp = Blueprint('demand_bp', __name__)
galactic_objects_bp = Blueprint('galactic_objects', __name__)


@users_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{
        "uuid": str(user.uuid),
        "username": user.username,
        "email": user.email,
        "permissions": user.permissions,
        "created_at": user.created_at
    } for user in users]
    return jsonify(users_list), 200

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password_hash = generate_password_hash(data.get('password'))
    permissions = data.get('permissions', [])

    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        permissions=permissions
    )

    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        return f"An exception occured: {str(e)}", 400

    return jsonify({
        "uuid": str(new_user.uuid),
        "username": new_user.username,
        "email": new_user.email,
        "permissions": new_user.permissions,
        "created_at": new_user.created_at
    }), 201


@galactic_objects_bp.route('/galactic_objects', methods=['GET'])
def get_galactic_objects():
    objects = GalacticObject.query.all()
    return jsonify([{
        "uuid": str(obj.uuid),
        "name": obj.name,
        "type_id": str(obj.type_id),
        "mass_kg": obj.mass_kg,
        "radius_km": obj.radius_km,
        "distance_from_earth_parsec": obj.distance_from_earth_parsec,
        "discovered_at": obj.discovered_at,
        "owner_id": str(obj.owner_id),
        "created_at": obj.created_at
    } for obj in objects]), 200

@galactic_objects_bp.route('/galactic_objects', methods=['POST'])
def create_galactic_object():
    data = request.get_json()
    
    # Fetch the GalacticObjectType by name
    object_type_name = data.get('type_name')
    object_type = GalacticObjectType.query.filter_by(name=object_type_name).first()
    
    if object_type is None:
        return jsonify({"error": "GalacticObjectType not found"}), 404
    
    new_object = GalacticObject(
        uuid=uuid4(),
        name=data.get('name'),
        type_id=object_type.uuid,
        mass_kg=data.get('mass_kg'),
        radius_km=data.get('radius_km'),
        distance_from_earth_parsec=data.get('distance_from_earth_parsec'),
        discovered_at=data.get('discovered_at'),
        owner_id=data.get('owner_id')
    )

    db.session.add(new_object)
    try:
        db.session.commit()
    except Exception as e:
        return f"An exception occurred: {str(e)}", 400

    return jsonify({
        "uuid": str(new_object.uuid),
        "name": new_object.name,
        "type_id": str(new_object.type_id),
        "mass_kg": new_object.mass_kg,
        "radius_km": new_object.radius_km,
        "distance_from_earth_parsec": new_object.distance_from_earth_parsec,
        "discovered_at": new_object.discovered_at,
        "owner_id": str(new_object.owner_id),
        "created_at": new_object.created_at
    }), 201

@galactic_objects_bp.route('/galactic_objects/<uuid:object_uuid>', methods=['DELETE'])
def delete_galactic_object(object_uuid):
    galactic_object = GalacticObject.query.get(object_uuid)
    if galactic_object is None:
        abort(404, "GalacticObject not found.")
    
    db.session.delete(galactic_object)
    try:
        db.session.commit()
    except Exception as e:
        return f"An exception occured: {str(e)}", 400

    return jsonify({"message": "GalacticObject deleted successfully"}), 204

@demand_bp.route('/demands', methods=['GET'])
def get_demands():
    demands = Demand.query.all()
    return jsonify([
        {
            "uuid": str(demand.uuid),
            "user_id": str(demand.user_id),
            "galactic_object_id": str(demand.galactic_object_id),
            "price_eur": demand.price_eur,
            "status": demand.status,
            "created_at": demand.created_at
        } for demand in demands
    ]), 200

@demand_bp.route('/demands', methods=['POST'])
def create_demand():
    data = request.get_json()

    new_demand = Demand(
        uuid=uuid4(),
        user_id=data.get('user_id'),
        galactic_object_id=data.get('galactic_object_id'),
        price_eur=data.get('price_eur'),
        status='pending'
    )

    db.session.add(new_demand)
    try:
        db.session.commit()
    except Exception as e:
        return f"An exception occurred: {str(e)}", 400

    return jsonify({
        "uuid": str(new_demand.uuid),
        "user_id": str(new_demand.user_id),
        "galactic_object_id": str(new_demand.galactic_object_id),
        "price_eur": new_demand.price_eur,
        "status": new_demand.status,
        "created_at": new_demand.created_at
    }), 201
