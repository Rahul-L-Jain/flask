from flask import Blueprint, request
from app.models import User
from app.extensions import db
from app.utils import success_response, error_response
from sqlalchemy.exc import IntegrityError

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [user.to_dict() for user in users]
    return success_response(user_list)

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(user.to_dict())

@user_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or 'first_name' not in data or 'last_name' not in data or 'email' not in data:
        return error_response("Missing required fields: first_name, last_name, email", 400)
    
    try:
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email']
        )
        db.session.add(new_user)
        db.session.commit()
        return success_response(new_user.to_dict(), "User created", 201)
    except IntegrityError:
        db.session.rollback()
        return error_response("Email already exists", 409)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
        
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400)
        
    # Check for primary key update attempt
    if 'id' in data and data['id'] != user_id:
        return error_response("Updating primary key is forbidden", 400)
        
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
             return error_response("Email already in use", 409)
        user.email = data['email']
        
    try:
        db.session.commit()
        return success_response(user.to_dict(), "User updated")
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
        
    try:
        db.session.delete(user)
        db.session.commit()
        return success_response(None, "User deleted", 204)
    except IntegrityError:
        # e.g. user has loans
        db.session.rollback()
        return error_response("Cannot delete user (likely has associated records)", 409)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)
