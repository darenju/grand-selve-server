from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from ..models.contact_card import ContactCard
from ..extensions import db

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

    return jsonify({ "message": "Merci de nous avoir contacté. Nous revenons vers vous rapidement." })
