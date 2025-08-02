from flask import Blueprint, jsonify, request
from sqlalchemy import func
from ..models.user import User, filter_users
from ..models.service import Service, filter_services
from ..models.member import Member, filter_members
from ..extensions import db
from ..auth import login_required
from ..email import send_email

home_bp = Blueprint('home', __name__, url_prefix='/')


@home_bp.route("/test", methods=["GET"])
def test():
  send_email("darenju@live.com")

  return jsonify({ "message": "OK" })


@home_bp.route('/stats', methods=['GET'])
@login_required()
def get_home_stats():
  users = db.session.query(func.count(User.id)).scalar()
  services = db.session.query(func.count(Service.id)).scalar()
  members = db.session.query(func.count(Member.id)).scalar()

  return jsonify({
    "users": users,
    "services": services,
    "members": members,
  })

@home_bp.route('/search', methods=['GET'])
@login_required()
def search():
  query = request.args.get("query")
  services = filter_services({ "*": query })
  users = filter_users({ "*": query })
  members = filter_members({
    "*": query,
    "sort_column": "name",
    "sort_direction": "desc",
    "per_page": 10,
    "page": 1,
  })

  return jsonify({
    "services": [s.to_dict() for s in services],
    "users": [u.to_dict() for u in users],
    "members": [m.to_dict() for m in members],
  }), 200
