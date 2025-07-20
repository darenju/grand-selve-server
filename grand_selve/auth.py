from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from grand_selve.models import User

def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    auth_header = request.headers.get('Authorization', None)

    if not auth_header or not auth_header.startswith('Bearer '):
      return jsonify({'message': 'Missing or invalid Authorization header'}), 401

    token = auth_header.split()[1]

    try:
      payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
      user_id = payload.get('sub')
      user = User.query.get(user_id)

      if not user:
        return jsonify({'message': 'User not found'}), 404

      g.current_user = user  # injecte l'utilisateur pour la route protégée

    except jwt.ExpiredSignatureError:
      return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError as e:
      print(str(e))
      return jsonify({'message': 'Invalid token'}), 401

    return f(*args, **kwargs)

  return decorated_function
  