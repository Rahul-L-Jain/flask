from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import User, Book, Loan, Sibling
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        if not first_name or not last_name or not email:
            flash('First and Last Name and Email are required', 'error')
        else:
            try:
                new_user = User(first_name=first_name, last_name=last_name, email=email)
                db.session.add(new_user)
                db.session.commit()
                flash('User created successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Email already exists.', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('main.users'))
        
    users = User.query.all()
    return render_template('users.html', users=users)

@main_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user_id:
                flash('Email already in use.', 'error')
                return redirect(url_for('main.edit_user', user_id=user_id))
            user.email = email
        
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
        return redirect(url_for('main.users'))
    
    return render_template('edit_user.html', user=user)

@main_bp.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Cannot delete user (has associated records).', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    return redirect(url_for('main.users'))

@main_bp.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        copies = request.form.get('available_copies')
        
        if not all([title, author, isbn, copies]):
            flash('All fields are required', 'error')
        else:
            try:
                new_book = Book(
                    title=title, 
                    author=author, 
                    isbn=isbn, 
                    available_copies=int(copies)
                )
                db.session.add(new_book)
                db.session.commit()
                flash('Book added successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('ISBN already exists.', 'error')
            except ValueError:
                flash('Available copies must be a number.', 'error')
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('main.books'))
        
    books = Book.query.all()
    return render_template('books.html', books=books)

@main_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        copies = request.form.get('available_copies')
        
        if title:
            book.title = title
        if author:
            book.author = author
        if isbn:
            existing = Book.query.filter_by(isbn=isbn).first()
            if existing and existing.id != book_id:
                flash('ISBN already in use.', 'error')
                return redirect(url_for('main.edit_book', book_id=book_id))
            book.isbn = isbn
        if copies:
            try:
                book.available_copies = int(copies)
            except ValueError:
                flash('Available copies must be a number.', 'error')
                return redirect(url_for('main.edit_book', book_id=book_id))
        
        try:
            db.session.commit()
            flash('Book updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating book: {str(e)}', 'error')
        return redirect(url_for('main.books'))
    
    return render_template('edit_book.html', book=book)

@main_bp.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    try:
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Cannot delete book (has associated loans).', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'error')
    return redirect(url_for('main.books'))

@main_bp.route('/loans', methods=['GET', 'POST'])
def loans():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        book_id = request.form.get('book_id')
        loan_id_to_return = request.form.get('loan_id')

        if loan_id_to_return:
            # Handle return
            loan = Loan.query.get(loan_id_to_return)
            if loan and not loan.returned_at:
                loan.returned_at = datetime.utcnow()
                if loan.book:
                    # Optional: increment available copies logic (if implemented)
                    pass
                try:
                    db.session.commit()
                    flash('Book returned successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error returning book: {str(e)}', 'error')
            return redirect(url_for('main.loans'))

        # Handle create
        if not user_id or not book_id:
             flash('User and Book are required', 'error')
        else:
            book = Book.query.get(book_id)
            if not book:
                flash('Book not found', 'error')
            elif book.available_copies < 1:
                flash('Book not available', 'error')
            else:
                try:
                    new_loan = Loan(user_id=user_id, book_id=book_id)
                    book.available_copies -= 1
                    db.session.add(new_loan)
                    db.session.commit()
                    flash('Loan created successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error creating loan: {str(e)}', 'error')
        return redirect(url_for('main.loans'))
        
    loans = Loan.query.join(User).join(Book).all()
    users = User.query.all()
    books = Book.query.filter(Book.available_copies > 0).all()
    return render_template('loans.html', loans=loans, users=users, books=books)

@main_bp.route('/siblings', methods=['GET', 'POST'])
def siblings():
    if request.method == 'POST':
        u1_id = request.form.get('user_id_1')
        u2_id = request.form.get('user_id_2')
        sibling_id_to_delete = request.form.get('delete_id')
        
        if sibling_id_to_delete:
            sib = Sibling.query.get(sibling_id_to_delete)
            if sib:
                try:
                    db.session.delete(sib)
                    db.session.commit()
                    flash('Sibling relationship removed', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(str(e), 'error')
            return redirect(url_for('main.siblings'))

        if u1_id == u2_id:
            flash('Cannot be siblings with oneself', 'error')
        else:
            u1, u2 = sorted([u1_id, u2_id])
            existing = Sibling.query.filter_by(user_id_1=u1, user_id_2=u2).first()
            if existing:
                flash('Relationship already exists', 'error')
            else:
                try:
                    new_sibling = Sibling(user_id_1=u1, user_id_2=u2)
                    db.session.add(new_sibling)
                    db.session.commit()
                    flash('Sibling relationship created!', 'success')
                except IntegrityError:
                    db.session.rollback() # Likely missing user
                    flash('User does not exist or ref constraint failure', 'error')
                except Exception as e:
                    db.session.rollback()
                    flash(str(e), 'error')
        return redirect(url_for('main.siblings'))
        
    siblings = Sibling.query.all()
    # Need to fetch users efficiently or lazy load
    # For display purposes, we might want names.
    # Let's perform a query join or just get all users
    users = User.query.all()
    # Map for easy lookup in template if needed (though we can query relationships if added to model)
    user_map = {u.id: u for u in users}
    
    return render_template('siblings.html', siblings=siblings, users=users, user_map=user_map)
