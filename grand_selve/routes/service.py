from flask import Blueprint, request, jsonify, g
from ..auth import login_required
from ..models.service import Service, filter_services
from ..models.user_service_role import ServiceRoleEnum, UserServiceRole
from ..models.forum_message import ForumMessage
from ..extensions import db, auto_cache, invalidate_cache

service_bp = Blueprint('service', __name__, url_prefix='/service')

@service_bp.route('', methods=['GET'])
@auto_cache()
@login_required()
def get_services():
  filters = request.args

  services = filter_services(filters or {})

  return jsonify([s.to_dict() for s in services])


@service_bp.route('/<service_id>', methods=['GET'])
@auto_cache()
@login_required()
def get_service(service_id):
  service = db.session.get(Service, int(service_id))
  
  if service is None:
    return jsonify({ "message": "Service introuvable." }), 404
  
  return jsonify(service.to_dict())


@service_bp.route('/<service_id>/details', methods=['GET'])
@auto_cache()
@login_required()
def get_service_details(service_id):
  service = db.session.get(Service, int(service_id))
  
  if service is None:
    return jsonify({ "message": "Service introuvable." }), 404
  
  return jsonify(service.to_dict(True))


@service_bp.route('', methods=['POST'])
@login_required(admin=True)
def create_service():
  data = request.get_json()

  service = Service(
    name=data.get("name"),
    description=data.get('description'),
    color=data.get('color'),
  )

  db.session.add(service)
  db.session.commit()

  invalidate_cache(["get_services"])

  return jsonify(service.to_dict()), 201


@service_bp.route('/<service_id>', methods=['PUT'])
@login_required(admin=True)
def edit_service(service_id):
  data = request.get_json()

  service = db.session.get(Service, int(service_id))
  service.name = data.get("name")
  service.description = data.get("description")
  service.color = data.get("color")

  db.session.commit()

  invalidate_cache(["get_services", f"get_service|service_id={service_id}", f"get_service_details|service_id={service_id}"])

  return jsonify(service.to_dict())


@service_bp.route("/<service_id>/user/<user_id>", methods=["POST"])
@login_required(admin=True)
def attach_user_to_service(service_id, user_id):
  data = request.get_json()

  link = UserServiceRole(
    user_id=int(user_id),
    service_id=int(service_id),
    role=ServiceRoleEnum(data.get("role")),
  )

  db.session.add(link)
  db.session.commit()

  invalidate_cache([f"get_service|service_id={service_id}", f"get_service_details|service_id={service_id}"])

  return jsonify({ "message": "OK" })


@service_bp.route("/link/<link_id>/<service_id>/user/<user_id>", methods=["PUT"])
@login_required(admin=True)
def edit_user_link(link_id, service_id, user_id):
  link = db.session.get(UserServiceRole, int(link_id))
  
  if link is None:
    return jsonify({ "message": "Lien introuvable." }), 404

  data = request.get_json()

  link.service_id = int(service_id)
  link.user_id = int(user_id)
  link.role = ServiceRoleEnum(data.get("role"))

  db.session.commit()

  invalidate_cache([f"get_service|service_id={service_id}", f"get_service_details|service_id={service_id}"])

  return jsonify({ "message": "OK" })


@service_bp.route("/link/<link_id>", methods=["DELETE"])
@login_required(admin=True)
def delete_user_link(link_id):
  link = db.session.get(UserServiceRole, int(link_id))

  if link is None:
    return jsonify({ "message": "Lien introuvable." }), 404

  db.session.delete(link)
  db.session.commit()

  invalidate_cache([f"get_service|service_id={link.service_id}", f"get_service_details|service_id={link.service_id}"])

  return jsonify({ "message": "OK" })


@service_bp.route("/<service_id>/forum", methods=["GET"])
@auto_cache()
@login_required()
def get_forum(service_id):
  forum_messages = db.session.query(ForumMessage).filter(ForumMessage.service_id == int(service_id)).all()

  return jsonify([fm.to_dict() for fm in forum_messages])


@service_bp.route("/<service_id>/forum", methods=["POST"])
@login_required()
def post_forum_message(service_id):
  data = request.get_json()
  user = g.current_user
  service = db.session.get(Service, int(service_id))

  if service is None:
    return jsonify({ "message": "Service introuvable." }), 404

  forum_message = ForumMessage(
    message=data.get("message"),
    service_id=service.id,
    user_id=user.id,
  )

  db.session.add(forum_message)
  db.session.commit()

  invalidate_cache([f"get_forum|service_id={service_id}"])

  return jsonify({ "message": "Message posté." }), 201
