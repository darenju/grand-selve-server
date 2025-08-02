import os
from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import jwt
from ..models import User
from ..extensions import db, allowed_file, get_extension
from ..auth import login_required
from .user import edit_user

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

def get_user_id():
  auth_header = request.headers.get('Authorization', None)
  token = auth_header.split()[1]

  try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = payload.get('sub')
    return user_id
  except jwt.InvalidTokenError:
    return jsonify({ "message": "Invalid refresh token." }), 401


@profile_bp.route('', methods=['PUT'])
@login_required()
def update_profile():
  user_id = get_user_id()

  return edit_user(int(user_id))


@profile_bp.route("/avatar", methods=["POST"])
@login_required()
def upload_avatar():
  user_id = get_user_id()
  user = User.query.get(user_id)

  file = request.files.get("avatar")

  if file and allowed_file(file.filename):
    filename = secure_filename(f"{uuid4().hex}.{get_extension(file.filename)}")
    file.save(os.path.join(current_app.config["AVATAR_UPLOAD_FOLDER"], filename))

    user.avatar_path = filename
    db.session.commit()

    return jsonify(user.to_dict())

  return jsonify({ "message": "Impossible de changer d'avatar." }), 400


@profile_bp.route("/avatar", methods=["DELETE"])
@login_required()
def delete_avatar():
  user_id = get_user_id()
  user = User.query.get(user_id)

  user.avatar_path = None
  db.session.commit()

  return jsonify(user.to_dict())

@profile_bp.route("/change-password", methods=["POST"])
@login_required()
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
