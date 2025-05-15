from flask import jsonify, request, Blueprint
from .models import db, Demand
from .camunda_client import CamundaClient
from .kafka_client import KafkaClient
from uuid import uuid4, UUID
import requests


demands_bp = Blueprint('demands', __name__)
camunda = CamundaClient()
kafka_client = KafkaClient()

@demands_bp.route('/demands', methods=['GET'])
def get_demands():
    user_id = request.args.get('user_id')
    query = Demand.query
    if user_id:
        try:
            query = query.filter_by(user_id=UUID(user_id))
        except Exception:
            return jsonify([]), 200
    demands = query.all()
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
        
        # Publish to Kafka
        demand_data = {
            "demand_id": str(new_demand.uuid),
            "user_id": user_id,
            "galactic_object_id": galactic_object_id,
            "price_eur": price_eur,
            "action": "create_demand"
        }
        
        kafka_result = kafka_client.publish_demand_request(demand_data)
        
        if not kafka_result:
            # Fall back to direct Camunda API if Kafka fails
            process_instance = camunda.start_demand_process(
                demand_id=str(new_demand.uuid),
                user_id=user_id,
                object_id=galactic_object_id,
                price=price_eur
            )
            process_instance_id = process_instance.get('id')
        else:
            # Update status to indicate it's been sent to Kafka
            kafka_client.publish_demand_status(
                str(new_demand.uuid), 
                "submitted_to_kafka",
                {"message": "Demand request sent to processing queue"}
            )
            process_instance_id = None
        
        return jsonify({
            "uuid": str(new_demand.uuid),
            "user_id": str(new_demand.user_id),
            "galactic_object_id": str(new_demand.galactic_object_id),
            "price_eur": new_demand.price_eur,
            "status": new_demand.status,
            "created_at": new_demand.created_at,
            "process_instance_id": process_instance_id,
            "kafka_published": kafka_result
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
        # Zisti, či ide o potvrdenie alebo odmietnutie (napr. podľa payloadu, default je potvrdenie)
        data = request.get_json(silent=True) or {}
        accepted = data.get('accepted', True)
        demand.status = 'accepted' if accepted else 'rejected'
        db.session.commit()
        
        # Dokonči všetky user tasky v Camunde (pre istotu)
        camunda_url = camunda.base_url
        resp = requests.get(f"{camunda_url}/engine-rest/task")
        if resp.status_code == 200:
            for task in resp.json():
                task_id = task.get('id')
                if task_id:
                    try:
                        camunda.complete_task(task_id, {"offerAccepted": {"value": accepted, "type": "Boolean"}})
                    except Exception:
                        pass

        # Vymaž všetky procesné inštancie (pre demo)
        resp = requests.get(f"{camunda_url}/engine-rest/process-instance")
        if resp.status_code == 200:
            for instance in resp.json():
                instance_id = instance.get('id')
                if instance_id:
                    requests.delete(f"{camunda_url}/engine-rest/process-instance/{instance_id}")
        
        return jsonify({
            "uuid": str(demand.uuid),
            "status": demand.status,
            "message": f"Demand {'accepted' if accepted else 'rejected'} successfully (all user tasks completed and all processes deleted for demo)"
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
