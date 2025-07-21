from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache

db = SQLAlchemy()

migrate = Migrate()

cache = Cache()

def parse_date(s):
    if s == "":
        return None

    try:
        return datetime.strptime(s, "%Y-%m-%d").date() if s else None
    except (ValueError, TypeError):
        return None
