from flask import Flask
from config import config
from app.extensions import db

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes.user_routes import user_bp
    from app.routes.book_routes import book_bp
    from app.routes.loan_routes import loan_bp
    from app.routes.sibling_routes import sibling_bp
    from app.routes.main_routes import main_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(loan_bp)
    app.register_blueprint(sibling_bp)
    app.register_blueprint(main_bp)
    
    # API Health Check
    @app.route('/health')
    def health():
        return {"status": "success", "message": "Library Management System API"}
        
    return app
