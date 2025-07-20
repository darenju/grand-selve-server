from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..auth import login_required
from ..models.member import Member, filter_members
from ..models.service_membership import Membership
from ..extensions import db, parse_date

member_bp = Blueprint("member", __name__, url_prefix="/member")


@member_bp.route("", methods=["GET"])
@login_required
def get_members():
    filters = request.args or {}

    filtered = filter_members(filters)

    result = {
        "members": [m.to_dict() for m in filtered.items],
        "pagination": list(filtered.iter_pages()),
    }

    return jsonify(result)


@member_bp.route("/<member_id>", methods=["GET"])
@login_required
def get_member(member_id):
    member = db.session.get(Member, int(member_id))

    if member is None:
        return jsonify({"message": "Participant introuvable."}), 404

    return jsonify(member.to_dict())


@member_bp.route("/<member_id>/details", methods=["GET"])
@login_required
def get_member_details(member_id):
    member = db.session.get(Member, int(member_id))

    if member is None:
        return jsonify({"message": "Participant introuvable."}), 404

    return jsonify(member.to_dict(True))

@member_bp.route("", methods=["POST"])
@login_required
def create_member():
    data = request.get_json()

    member = Member(
        email=data.get("email"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        gender=data.get("gender"),
        date_of_birth=parse_date(data.get("date_of_birth")),

        created_by_user_id=g.current_user.id,
        # created_at=None,
        notes=data.get("notes"),

        telephone=data.get("telephone"),
        address=data.get("address"),
        zipcode=data.get("zipcode"),
        city=data.get("city"),
    )

    db.session.add(member)
    db.session.commit()

    return jsonify(member.to_dict()), 201


@member_bp.route("/<member_id>", methods=["PUT"])
@login_required
def edit_member(member_id):
    member = Member.query.get(member_id)

    if not member:
        return jsonify({ "message": "Participant introuvable." }), 404

    data = request.get_json()

    date_of_birth = data.get("date_of_birth")
    baptism = data.get("baptism")
    confirmation = data.get("confirmation")
    first_communion = data.get("first_communion")
    marriage = data.get("marriage")

    member.first_name = data.get("first_name")
    member.last_name = data.get("last_name")
    member.gender = data.get("gender")
    member.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d") if date_of_birth != "" else None

    member.notes = data.get("notes")

    member.telephone = data.get("telephone")
    member.address = data.get("address")
    member.zipcode = data.get("zipcode")
    member.city = data.get("city")

    member.baptism = datetime.strptime(baptism, "%Y-%m-%d").date() if baptism != "" else None
    member.confirmation = datetime.strptime(confirmation, "%Y-%m-%d").date() if confirmation != "" else None
    member.first_communion = datetime.strptime(first_communion, "%Y-%m-%d").date() if data.get(
        "first_communion") != "" else None
    member.marriage = datetime.strptime(marriage, "%Y-%m-%d").date() if marriage != "" else None

    db.session.commit()

    return jsonify(member.to_dict())


@member_bp.route("/<member_id>/service/<service_id>", methods=["POST"])
@login_required
def attach_member_to_service(service_id, member_id):
  service_membership = Membership(
    member_id=int(member_id),
    service_id=int(service_id),
    invited_by_id=g.current_user.id,
  )

  try:
    db.session.add(service_membership)
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({ "message": "Ce participant fait déjà partie de ce service." }), 403

  return jsonify({ "message": "OK" })


@member_bp.route("/<member_id>/service/<service_id>", methods=["DELETE"])
@login_required
def delete_user_membership(service_id, member_id):
  membership = Membership.query.filter(
    Membership.service_id == int(service_id),
    Membership.member_id == int(member_id)
  ).first()

  if membership is None:
    return jsonify({ "message": "Lien introuvable." }), 404

  membership.left = datetime.now()

  db.session.commit()

  return jsonify({ "message": "OK" })


@member_bp.route("/<member_id>/service/<service_id>/recreate", methods=["POST"])
@login_required
def recreate_user_membership(service_id, member_id):
  membership = Membership.query.filter(
    Membership.service_id == int(service_id),
    Membership.member_id == int(member_id)
  ).first()

  if membership is None:
    return jsonify({ "message": "Lien introuvable." }), 404

  membership.joined = datetime.now()
  membership.left = None

  db.session.commit()

  return jsonify({ "message": "OK" })
