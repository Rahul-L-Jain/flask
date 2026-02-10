from flask import Blueprint, request, jsonify
from app.models import Book
from app.extensions import db
from app.utils import success_response, error_response
from sqlalchemy.exc import IntegrityError

book_bp = Blueprint('books', __name__, url_prefix='/books')

@book_bp.route('', methods=['GET'])
def get_books():
    books = Book.query.all()
    book_list = [book.to_dict() for book in books]
    return jsonify({"status": "success", "data": book_list}), 200

@book_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
    return jsonify({"status": "success", "data": book.to_dict()}), 200

@book_bp.route('', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or 'title' not in data or 'author' not in data or 'isbn' not in data:
        return jsonify({"status": "error", "message": "Missing required fields: title, author, isbn"}), 400
    
    try:
        new_book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            available_copies=data.get('available_copies', 1)
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"status": "success", "data": new_book.to_dict(), "message": "Book created"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "ISBN already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@book_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
        
    if 'id' in data and data['id'] != book_id:
        return jsonify({"status": "error", "message": "Updating primary key is forbidden"}), 400
        
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'isbn' in data:
        existing_book = Book.query.filter_by(isbn=data['isbn']).first()
        if existing_book and existing_book.id != book_id:
             return jsonify({"status": "error", "message": "ISBN already in use"}), 409
        book.isbn = data['isbn']
    if 'available_copies' in data:
        book.available_copies = data['available_copies']
        
    try:
        db.session.commit()
        return jsonify({"status": "success", "data": book.to_dict(), "message": "Book updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@book_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
        
    try:
        db.session.delete(book)
        db.session.commit()
        return '', 204
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Cannot delete book (likely has associated loans)"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
