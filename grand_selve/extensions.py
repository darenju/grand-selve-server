from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

migrate = Migrate()

def parse_date(s):
    print(s)
    if s == "":
        return None

    try:
        return datetime.strptime(s, "%Y-%m-%d").date() if s else None
    except (ValueError, TypeError):
        return None
