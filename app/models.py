from datetime import datetime
from app.extensions import db
from sqlalchemy import CheckConstraint

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship('Loan', backref='user', lazy=True)
    
    # Sibling relationships
    # This is tricky because it's self-referential many-to-many via Sibling table
    # but we handle it via queries or helper methods usually.
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    available_copies = db.Column(db.Integer, default=1)

    loans = db.relationship('Loan', backref='book', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'available_copies': self.available_copies
        }

class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrowed_at = db.Column(db.DateTime, default=datetime.utcnow)
    returned_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrowed_at': self.borrowed_at.isoformat() if self.borrowed_at else None,
            'returned_at': self.returned_at.isoformat() if self.returned_at else None
        }

class Sibling(db.Model):
    __tablename__ = 'siblings'
    
    sibling_id = db.Column(db.Integer, primary_key=True)
    user_id_1 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id_2 = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    __table_args__ = (
        CheckConstraint('user_id_1 != user_id_2', name='check_sibling_not_same'),
        db.UniqueConstraint('user_id_1', 'user_id_2', name='unique_sibling_pair'),
    )

    def to_dict(self):
        return {
            'sibling_id': self.sibling_id,
            'user_id_1': self.user_id_1,
            'user_id_2': self.user_id_2
        }
