from flask import Blueprint, request, jsonify
from app.models import Sibling, User
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from app.utils import success_response, error_response

sibling_bp = Blueprint('siblings', __name__, url_prefix='/siblings')

@sibling_bp.route('', methods=['GET'])
def get_siblings():
    siblings = Sibling.query.all()
    sibling_list = [sibling.to_dict() for sibling in siblings]
    return success_response(sibling_list)

@sibling_bp.route('/<int:sibling_id>', methods=['GET'])
def get_sibling(sibling_id):
    sibling = Sibling.query.get(sibling_id)
    if not sibling:
        return error_response("Sibling relationship not found", 404)
    return success_response(sibling.to_dict())

@sibling_bp.route('', methods=['POST'])
def create_sibling():
    data = request.get_json()
    if not data or 'user_id_1' not in data or 'user_id_2' not in data:
        return error_response("Missing required fields: user_id_1, user_id_2", 400)
    
    id1 = data['user_id_1']
    id2 = data['user_id_2']
    
    if id1 == id2:
        return error_response("Cannot be siblings with oneself", 400)
        
    # Enforce order to ensure uniqueness bidirectional check (A-B == B-A)
    # Important: sort the IDs
    u1, u2 = sorted([id1, id2])
    
    # Check if they exist (requires checking the original IDs or the sorted ones)
    user1 = User.query.get(u1)
    user2 = User.query.get(u2)
    
    if not user1 or not user2:
        return error_response("One or both users not found", 404)
        
    # Check for existing
    existing = Sibling.query.filter_by(user_id_1=u1, user_id_2=u2).first()
    if existing:
        return error_response("Sibling relationship already exists", 409)
        
    try:
        new_sibling = Sibling(user_id_1=u1, user_id_2=u2)
        db.session.add(new_sibling)
        db.session.commit()
        return success_response(new_sibling.to_dict(), "Sibling relationship created", 201)
    except IntegrityError:
        db.session.rollback()
        # This catch is mostly a safeguard, we already checked manually above
        return error_response("Database integrity error", 409)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@sibling_bp.route('/<int:sibling_id>', methods=['PUT'])
def update_sibling(sibling_id):
    sibling = Sibling.query.get(sibling_id)
    if not sibling:
        return error_response("Sibling relationship not found", 404)
        
    data = request.get_json()
    if not data:
        return error_response("No data provided", 400)

    if 'sibling_id' in data and data['sibling_id'] != sibling_id:
        return error_response("Updating primary key is forbidden", 400)

    # Determine potential new values
    current_u1 = sibling.user_id_1
    current_u2 = sibling.user_id_2
    
    new_u1_req = data.get('user_id_1', current_u1)
    new_u2_req = data.get('user_id_2', current_u2)
    
    if new_u1_req == new_u2_req:
        return error_response("Cannot be siblings with oneself", 400)
        
    # Sort them to maintain invariant in persistence
    final_u1, final_u2 = sorted([new_u1_req, new_u2_req])
    
    # Verify existence if changed
    if final_u1 != current_u1 or final_u2 != current_u2:
        # Check if users exist only if they are new IDs
        # To be safe, check both.
        if not User.query.get(final_u1) or not User.query.get(final_u2):
             return error_response("One or both users not found", 404)
             
        # Check uniqueness against OTHER records
        existing = Sibling.query.filter_by(user_id_1=final_u1, user_id_2=final_u2).first()
        if existing and existing.sibling_id != sibling_id:
            return error_response("Sibling relationship already exists", 409)
            
        sibling.user_id_1 = final_u1
        sibling.user_id_2 = final_u2
        
    try:
        db.session.commit()
        return success_response(sibling.to_dict(), "Sibling relationship updated")
    except IntegrityError:
        db.session.rollback()
        return error_response("Database integrity error", 409)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@sibling_bp.route('/<int:sibling_id>', methods=['DELETE'])
def delete_sibling(sibling_id):
    sibling = Sibling.query.get(sibling_id)
    if not sibling:
        return error_response("Sibling relationship not found", 404)
        
    try:
        db.session.delete(sibling)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)
