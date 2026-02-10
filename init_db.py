import os
import pymysql
from dotenv import load_dotenv
from config import Config
from app.extensions import db
from app import create_app

load_dotenv()

def create_database():
    """Create the database if it doesn't exist using plain pymysql."""
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'password')
    port = int(os.getenv('DB_PORT', '3306'))
    db_name = os.getenv('DB_NAME', 'library_db')

    print(f"Connecting to MySQL at {host}:{port}...")
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )

    try:
        with connection.cursor() as cursor:
            print(f"Creating database '{db_name}' if it doesn't exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        print("Database checked/created successfully.")
    finally:
        connection.close()

def initialize_tables():
    """Initialize all tables using SQLAlchemy models."""
    app = create_app('production' if os.getenv('FLASK_CONFIG') == 'production' else 'development')
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Initializing tables...")
        db.create_all()
        print("Tables initialized successfully.")

if __name__ == "__main__":
    try:
        create_database()
        initialize_tables()
        print("\nInitialization Complete!")
    except Exception as e:
        print(f"\nError initializing database: {e}")
