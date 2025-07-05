from flask import Flask, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from extensions import db, mail

# Load environment variables from .env file
load_dotenv()

# Global db object
db = SQLAlchemy()

# Initialize the app and db
def create_app():
    app = Flask(__name__)

    # Configuration settings
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_strong_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///project.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    app.config['REPORT_FOLDER'] = os.path.join(app.root_path, 'static', 'reports')


    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

   
    
    # Set UPLOAD_FOLDER and ensure the directory exists
    upload_folder = os.path.join(os.getcwd(), 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Define REPORT_FOLDER and ensure the directory exists
    report_folder = os.path.join(os.getcwd(), 'static', 'reports')
    os.makedirs(report_folder, exist_ok=True)
    app.config['REPORT_FOLDER'] = report_folder

    static_folder = os.path.join(os.getcwd(), 'static', 'css')
    os.makedirs(static_folder, exist_ok=True)
    app.config['STATIC_FOLDER'] = static_folder

    # Initialize the db with the app instance
    db.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)

    # Register Blueprints
    from Blueprint.login import login_bp
    from Blueprint.dashboard import dashboard_bp
    from Blueprint.generate import generate_bp
    from Blueprint.upload import upload_bp
    from Blueprint.validation import validate_bp
    from Blueprint.home import home_bp

    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(generate_bp, url_prefix='/generate')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(validate_bp, url_prefix='/validate')
    app.register_blueprint(home_bp, url_prefix='/home') 

    # Route redirect to home page
    @app.route("/")
    def home():
        return redirect(url_for('home.home'))

    return app

# Running the app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
