from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash

from ..auth import login_required
from ..models.user import User, UserRoleEnum, filter_users
from ..extensions import db, parse_date, auto_cache, invalidate_cache

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("", methods=["GET"])
@auto_cache()
@login_required()
def get_users():
  filters = request.args

  print(filters)

  users = filter_users(filters or {})

  return jsonify([u.to_dict() for u in users])


@user_bp.route("/<user_id>", methods=["GET"])
@auto_cache()
@login_required()
def get_user(user_id):
  user = db.session.get(User, int(user_id))
  
  if user is None:
    return jsonify({ "message": "Animateur introuvable." }), 404
  
  return jsonify(user.to_dict())


@user_bp.route("/<user_id>/details", methods=["GET"])
@auto_cache()
@login_required()
def get_user_details(user_id):
  user = db.session.get(User, int(user_id))
  
  if user is None:
    return jsonify({ "message": "Animateur introuvable." }), 404
  
  return jsonify(user.to_dict(True))


@user_bp.route("", methods=["POST"])
@login_required(admin=True)
def create_user():
  data = request.get_json()

  user = User(
    email=data.get("email"),
    password_hash=generate_password_hash("jesus"),
    first_name=data.get("first_name"),
    last_name=data.get("last_name"),
    gender=data.get("gender"),
    date_of_birth=parse_date(data.get("date_of_birth")),

    telephone = data.get("telephone"),
    address = data.get("address"),
    zipcode = data.get("zipcode"),
    city = data.get("city"),

    baptism=parse_date(data.get("baptism")),
    confirmation=parse_date(data.get("confirmation")),
    first_communion=parse_date(data.get("first_communion")),
    marriage=parse_date(data.get("marriage")),
    ordination=parse_date(data.get("ordination")),

    role=UserRoleEnum("user"),
  )

  db.session.add(user)
  db.session.commit()

  # Invalidate cache.
  invalidate_cache(["get_users"])

  return jsonify(user.to_dict()), 201


@user_bp.route("/<user_id>", methods=["PUT"])
@login_required(admin=True)
def edit_user(user_id):
  user = User.query.get(user_id)

  if not user:
    return jsonify({'message': 'User not found'}), 404

  data = request.get_json()

  date_of_birth = data.get('date_of_birth')
  baptism = data.get('baptism')
  confirmation = data.get('confirmation')
  first_communion = data.get('first_communion')
  marriage = data.get('marriage')
  ordination = data.get('ordination')

  user.first_name = data.get('first_name')
  user.last_name = data.get('last_name')
  user.gender = data.get('gender')
  user.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d") if date_of_birth != '' else None

  user.telephone = data.get("telephone")
  user.address = data.get("address")
  user.zipcode = data.get("zipcode")
  user.city = data.get("city")
  
  user.baptism = datetime.strptime(baptism, "%Y-%m-%d").date() if baptism != '' else None
  user.confirmation = datetime.strptime(confirmation, "%Y-%m-%d").date() if confirmation != '' else None
  user.first_communion = datetime.strptime(first_communion, "%Y-%m-%d").date() if data.get('first_communion') != '' else None
  user.marriage = datetime.strptime(marriage, "%Y-%m-%d").date() if marriage != '' else None
  user.ordination = datetime.strptime(ordination, "%Y-%m-%d").date() if ordination != '' else None

  user.role = UserRoleEnum(data.get("role"))

  db.session.commit()
  
  # Invalidate cache.
  invalidate_cache(["get_users", f"get_user|user_id={user_id}", f"get_user_details|user_id={user_id}"])

  return jsonify(user.to_dict())
