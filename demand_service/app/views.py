from flask import jsonify, request, Blueprint
from .models import db, Demand
from .camunda_client import CamundaClient
from uuid import uuid4

demands_bp = Blueprint('demands', __name__)
camunda = CamundaClient()

@demands_bp.route('/demands', methods=['GET'])
def get_demands():
    demands = Demand.query.all()
    demands_list = [{
        "uuid": str(demand.uuid),
        "user_id": str(demand.user_id),
        "galactic_object_id": str(demand.galactic_object_id),
        "price_eur": demand.price_eur,
        "status": demand.status,
        "created_at": demand.created_at
    } for demand in demands]
    return jsonify(demands_list), 200

@demands_bp.route('/demands', methods=['POST'])
def create_demand():
    data = request.get_json()
    
    user_id = data.get('user_id')
    galactic_object_id = data.get('galactic_object_id')
    price_eur = data.get('price_eur')
    
    if not all([user_id, galactic_object_id, price_eur]):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_demand = Demand(
        uuid=uuid4(),
        user_id=user_id,
        galactic_object_id=galactic_object_id,
        price_eur=price_eur,
        status='pending'
    )
    
    db.session.add(new_demand)
    try:
        db.session.commit()
        
        # Start Camunda process
        process_instance = camunda.start_demand_process(
            demand_id=str(new_demand.uuid),
            user_id=user_id,
            object_id=galactic_object_id,
            price=price_eur
        )
        
        return jsonify({
            "uuid": str(new_demand.uuid),
            "user_id": str(new_demand.user_id),
            "galactic_object_id": str(new_demand.galactic_object_id),
            "price_eur": new_demand.price_eur,
            "status": new_demand.status,
            "created_at": new_demand.created_at,
            "process_instance_id": process_instance.get('id')
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@demands_bp.route('/demands/<uuid:uuid>/confirm', methods=['POST'])
def confirm_demand(uuid):
    demand = Demand.query.filter_by(uuid=uuid).first()
    if not demand:
        return jsonify({"error": "Demand not found"}), 404
    
    if demand.status != 'pending':
        return jsonify({"error": "Demand is not in pending status"}), 400
    
    try:
        # Update demand status
        demand.status = 'confirmed'
        db.session.commit()
        
        return jsonify({
            "uuid": str(demand.uuid),
            "status": demand.status,
            "message": "Demand confirmed successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@demands_bp.route('/demands/<uuid:uuid>', methods=['DELETE'])
def delete_demand(uuid):
    demand = Demand.query.filter_by(uuid=uuid).first()
    if not demand:
        return jsonify({"error": "Demand not found"}), 404
    
    try:
        db.session.delete(demand)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@demands_bp.route('/tasks', methods=['GET'])
def get_user_tasks():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    try:
        tasks = camunda.get_user_tasks(user_id)
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@demands_bp.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    data = request.get_json()
    variables = data.get('variables', {})
    
    try:
        camunda.complete_task(task_id, variables)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500
