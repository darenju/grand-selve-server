import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate
from .models import *
from .routes.auth import auth_bp
from .routes.home import home_bp
from .routes.member import member_bp
from .routes.profile import profile_bp
from .routes.service import service_bp
from .routes.user import user_bp
from .auth import login_required

load_dotenv()

def create_app():
  env = os.getenv('FLASK_ENV', 'development').lower()
  is_production = env == 'production'

  app = Flask(__name__)
  app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
  app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://grand_selve:{os.getenv("DATABASE_PASSWORD")}@localhost:5432/grand_selve"
  app.config["UPLOAD_FOLDER"] = os.getenv("AVATAR_UPLOAD_FOLDER")
  app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900        # 15 minutes
  app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800     # 7 jours
  
  CORS(app)

  db.init_app(app)

  if is_production:
    migrate.init_app(app, db, directory=os.path.join(os.path.dirname(__file__), '../migrations'))
  else:
    migrate.init_app(app, db)

  app.register_blueprint(auth_bp)
  app.register_blueprint(home_bp)
  app.register_blueprint(profile_bp)
  app.register_blueprint(service_bp)
  app.register_blueprint(user_bp)
  app.register_blueprint(member_bp)
  
  return app
