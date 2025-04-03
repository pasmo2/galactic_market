from flask import jsonify, request, Blueprint, abort
from models import db, User, GalacticObject, GalacticObjectType, Demand
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from sqlalchemy.orm import joinedload

users_bp = Blueprint('users', __name__)

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
    password = data.get('password')
    permissions = data.get('permissions', [])

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Username or email already exists."}), 409

    password_hash = generate_password_hash(password)

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
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "uuid": str(new_user.uuid),
        "username": new_user.username,
        "email": new_user.email,
        "permissions": new_user.permissions,
        "created_at": new_user.created_at
    }), 201


@users_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({
        "uuid": str(user.uuid),
        "username": user.username,
        "permissions": user.permissions
    }), 200