from flask import Blueprint, jsonify, request
from sqlalchemy import func
from ..models.user import User, filter_users
from ..models.service import Service, filter_services
from ..extensions import db
from ..auth import login_required

home_bp = Blueprint('home', __name__, url_prefix='/')

@home_bp.route('/stats', methods=['GET'])
@login_required
def get_home_stats():
  users = db.session.query(func.count(User.id)).scalar()
  services = db.session.query(func.count(Service.id)).scalar()

  return jsonify({
    "users": users,
    "services": services,
  })

@home_bp.route('/search', methods=['GET'])
@login_required
def search():
  query = request.args.get("query")
  services = filter_services({ "*": query })
  users = filter_users({ "*": query })

  return jsonify({
    "services": [s.to_dict() for s in services],
    "users": [u.to_dict() for u in users]
  }), 200
