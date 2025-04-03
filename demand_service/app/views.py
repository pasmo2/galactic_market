from flask import jsonify, request, Blueprint, abort
from models import db, User, GalacticObject, GalacticObjectType, Demand
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from sqlalchemy.orm import joinedload


demand_bp = Blueprint('demand_bp', __name__)

@demand_bp.route('/demands', methods=['GET'])
def get_demands():
    user_id = request.args.get('user_id')

    query = Demand.query
    if user_id:
        query = query.filter_by(user_id=user_id)

    demands = query.all()

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

@demand_bp.route('/demands/<uuid:demand_id>/confirm', methods=['POST'])
def confirm_demand(demand_id):
    demand = Demand.query.get(demand_id)
    if not demand:
        return jsonify({"error": "Demand not found"}), 404

    if demand.status != 'pending':
        return jsonify({"error": "Demand is not pending"}), 400

    # Fetch the related galactic object
    galactic_object = GalacticObject.query.get(demand.galactic_object_id)
    if not galactic_object:
        return jsonify({"error": "Galactic object not found"}), 404

    # Transfer ownership
    galactic_object.owner_id = demand.user_id

    # Optional: Reject other pending demands for the same object
    other_demands = Demand.query.filter(
        Demand.galactic_object_id == demand.galactic_object_id,
        Demand.uuid != demand.uuid,
        Demand.status == 'pending'
    ).all()
    for other in other_demands:
        other.status = 'rejected'

    db.session.delete(demand)

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Demand confirmed, ownership transferred, and demand removed",
        "new_owner_id": str(galactic_object.owner_id),
        "object_id": str(galactic_object.uuid)
    }), 200


@demand_bp.route('/demands/<uuid:demand_id>', methods=['DELETE'])
def delete_demand(demand_id):
    demand = Demand.query.get(demand_id)
    if not demand:
        return jsonify({"error": "Demand not found"}), 404

    db.session.delete(demand)
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Demand deleted"}), 204
