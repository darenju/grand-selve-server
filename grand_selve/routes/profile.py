from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
from ..extensions import db
from ..auth import login_required
from .user import edit_user

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('', methods=['PUT'])
@login_required
def update_profile():
  auth_header = request.headers.get('Authorization', None)
  token = auth_header.split()[1]

  try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = payload.get('sub')

    return edit_user(int(user_id))

  except jwt.InvalidTokenError:
    return jsonify({ "message": "Invalid refresh token." }), 401

@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
  data = request.get_json()

  user = g.current_user
  current_password = data.get("current_password")
  new_password = data.get("new_password")
  new_password_confirmation = data.get("new_password_confirmation")

  if user.changed_first_password and not check_password_hash(user.password_hash, current_password):
    return jsonify({ "message": "Mot de passe incorrect." }), 401

  if new_password != new_password_confirmation:
    return jsonify({ "message": "Le nouveau mot de passe et la confirmation ne correspondent pas." }), 401

  user.changed_first_password = True
  user.password_hash = generate_password_hash(new_password)

  db.session.commit()

  return jsonify({ "message": "Votre mot de passe a bien été modifié." })
