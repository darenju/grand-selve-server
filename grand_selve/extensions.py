from functools import wraps
from flask import request
import hashlib
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

def make_key(name, *args, **kwargs):
    parts = [name]

    if request.view_args:
        parts.extend(f"{k}={v}" for k, v in sorted(request.view_args.items()))

    raw_key = "|".join(parts)
    return hashlib.sha1(raw_key.encode()).hexdigest()


def auto_cache():
    def decorator(fn):
        @cache.cached(make_cache_key=lambda *args, **kwargs: make_key(fn. __name__))
        @wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapped
    return decorator

def invalidate_cache(entries):
    for entry in entries:
        key = make_key(entry)
        cache.delete(key)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return '.' in filename and get_extension(filename) in ALLOWED_EXTENSIONS
