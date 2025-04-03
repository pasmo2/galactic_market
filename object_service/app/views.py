from flask import jsonify, request, Blueprint, abort
from models import db, GalacticObject, Demand, GalacticObjectType
from sqlalchemy.orm import joinedload
from uuid import uuid4

galactic_objects_bp = Blueprint('galactic_objects', __name__)

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

@galactic_objects_bp.route('/galactic_objects_search', methods=['GET'])
def create_galactic_object():
    name_query = request.args.get('name')

    query = GalacticObject.query
    if name_query:
        query = query.filter(GalacticObject.name.ilike(f'%{name_query}%'))

    objects = query.all()

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

@galactic_objects_bp.route('/add_galactic_objects', methods=['POST'])
def add_galactic_object():
    data = request.get_json()

    # Get type_name and fetch the actual type UUID
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
        return jsonify({"error": f"An exception occurred: {str(e)}"}), 400

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


@galactic_objects_bp.route('/galactic_objects/owned_by/<uuid:user_id>', methods=['GET'])
def get_owned_objects(user_id):
    # Eager-load demands for each object
    objects = GalacticObject.query.options(joinedload(GalacticObject.demands)).filter_by(owner_id=user_id).all()

    result = []
    for obj in objects:
        has_offer = Demand.query.filter_by(galactic_object_id=obj.uuid).count() > 0
        result.append({
            "uuid": str(obj.uuid),
            "name": obj.name,
            "has_offer": has_offer
        })

    return jsonify(result), 200