from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from ..models.contact_card import ContactCard
from ..extensions import db, auto_cache, invalidate_cache
from ..auth import login_required

contact_card_bp = Blueprint("contact_card", __name__, url_prefix="/contact")


@contact_card_bp.route("", methods=["POST"])
def create_contact_card():
    data = request.get_json()

    contact_card = ContactCard(
        name=data.get("name"),
        interest=data.get("interest"),
        telephone=data.get("telephone"),
        email=data.get("email"),
        notes=data.get("notes"),
    )

    try:
        db.session.add(contact_card)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        return jsonify({ "message": "Vous avez déjà pris contact." })

    invalidate_cache(["get_contact_cards"])

    return jsonify({ "message": "Merci de nous avoir contacté. Nous revenons vers vous rapidement." })


@contact_card_bp.route("", methods=["GET"])
@auto_cache()
@login_required()
def get_contact_cards():
    contact_cards = ContactCard.query.filter_by(handled=None).all()

    return jsonify([cc.to_dict() for cc in contact_cards])

@contact_card_bp.route("/<contact_card_id>", methods=["GET"])
@auto_cache()
@login_required()
def get_contact_card(contact_card_id):
    contact_card = ContactCard.query.get(contact_card_id)

    if contact_card is None:
        return jsonify({ "message": "Prise de contact introuvable." }), 404

    return jsonify(contact_card.to_dict())
