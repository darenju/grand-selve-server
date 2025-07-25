from flask import Blueprint, request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from ..models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  user = User.query.filter_by(email=data.get('email')).first()

  if user and check_password_hash(user.password_hash, data.get('password')):
    access_token = jwt.encode({
      'sub': str(user.id),
      'exp': datetime.now() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    refresh_token_ = jwt.encode({
      'sub': str(user.id),
      'exp': datetime.now() + timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
      'user': user.to_dict(),
      'access_token': access_token,
      'refresh_token': refresh_token_,
    })

  return jsonify({ "message": "Identifiants invalides" }), 401

@auth_bp.route('/refresh_token', methods=['POST'])
def refresh_token():
  data = request.get_json()
  token = data.get('refresh_token')

  if not token:
    return jsonify({'message': 'Missing refresh token'}), 400

  try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = payload['sub']

    user = User.query.get(int(user_id))

    if user:
      new_access_token = jwt.encode({
        'sub': str(user_id),
        'exp': datetime.now() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
      }, current_app.config['SECRET_KEY'], algorithm='HS256')

      return jsonify({
        'access_token': new_access_token,
        'user': user.to_dict(),
      }), 200
    else:
      return jsonify({ 'message': 'User not found' }), 404

  except jwt.ExpiredSignatureError:
      return jsonify({'message': 'Refresh token expired'}), 401
  except jwt.InvalidTokenError:
      return jsonify({'message': 'Invalid refresh token'}), 401