from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_, and_, func
from sqlalchemy.orm import aliased
from ..models.private_message import PrivateMessage
from ..auth import login_required
from ..extensions import db

def get_messages_with_user(user_id):
    return PrivateMessage.query.filter(
        and_(
            or_(
                PrivateMessage.to_user_id == g.current_user.id,
                PrivateMessage.to_user_id == int(user_id),
                ),
            or_(
                PrivateMessage.from_user_id == int(user_id),
                PrivateMessage.from_user_id == g.current_user.id
            ),
            or_(
                and_(
                    PrivateMessage.from_user_id == g.current_user.id,
                    PrivateMessage.deleted_sender == False
                ),
                and_(
                    PrivateMessage.to_user_id == g.current_user.id,
                    PrivateMessage.deleted_recipient == False
                )
            )
        )
    )

def get_messages_from_user(user_id):
    return PrivateMessage.query.filter(
        PrivateMessage.from_user_id == g.current_user.id,
        PrivateMessage.to_user_id == int(user_id),
        )


def get_messages_to_user(user_id):
    return PrivateMessage.query.filter(
        PrivateMessage.from_user_id == int(user_id),
        PrivateMessage.to_user_id == g.current_user.id,
        )


private_message_bp = Blueprint("private_message", __name__, url_prefix="/private_message")

@private_message_bp.route("", methods=["GET"])
@login_required()
def get_private_messages():
    latest_message_subq = (
        db.session.query(
            func.least(PrivateMessage.from_user_id, PrivateMessage.to_user_id).label("user1"),
            func.greatest(PrivateMessage.from_user_id, PrivateMessage.to_user_id).label("user2"),
            func.max(PrivateMessage.sent).label("last_sent"),
        )
        .filter(
            or_(
                and_(
                    PrivateMessage.to_user_id == g.current_user.id,
                    PrivateMessage.deleted_recipient == False,
                ),
                and_(
                    PrivateMessage.from_user_id == g.current_user.id,
                    PrivateMessage.deleted_sender == False,
                ),
            )
        )
        .group_by(
            func.least(PrivateMessage.from_user_id, PrivateMessage.to_user_id),
            func.greatest(PrivateMessage.from_user_id, PrivateMessage.to_user_id),
        )
    ).subquery()

    # Alias pour la table PrivateMessage
    messages = aliased(PrivateMessage)

    # Rejoindre la table PrivateMessage avec la sous-requête pour récupérer le message correspondant au max(sent)
    query = (
        db.session.query(messages)
        .join(
            latest_message_subq,
            and_(
                func.least(messages.from_user_id, messages.to_user_id) == latest_message_subq.c.user1,
                func.greatest(messages.from_user_id, messages.to_user_id) == latest_message_subq.c.user2,
                messages.sent == latest_message_subq.c.last_sent,
            )
        )
        .order_by(messages.sent.desc())
    )

    private_messages = query.all()

    return jsonify([pm.to_dict() for pm in private_messages])


@private_message_bp.route("/read/<user_id>", methods=["PUT"])
@login_required()
def mark_as_read(user_id):
    read = request.get_json().get("read")

    # Mark as unread for the sender.
    last_msg_sender = get_messages_from_user(user_id).order_by(PrivateMessage.sent.desc()).first()

    if last_msg_sender:
        last_msg_sender.read_sender = read

    # Mark as unread for the recipient.
    last_msg_recipient = get_messages_to_user(user_id).order_by(PrivateMessage.sent.desc()).first()

    if last_msg_recipient:
        last_msg_recipient.read = read

    db.session.commit()

    return jsonify({ "message": "OK" })


@private_message_bp.route("/<user_id>", methods=["DELETE"])
@login_required()
def mark_as_deleted(user_id):
    # Mark as undeleted for the sender.
    get_messages_from_user(user_id).update({
        "deleted_sender": True
    })

    # Mark as undeleted for the recipient.
    msg_recipient = get_messages_to_user(user_id).update({
        "deleted_recipient": True
    })

    db.session.commit()

    return jsonify({ "message": "OK" })


@private_message_bp.route("/<user_id>", methods=["GET"])
@login_required()
def get_conversation(user_id):
    messages = get_messages_with_user(user_id).order_by(PrivateMessage.sent.desc()).all()

    return jsonify([m.to_dict() for m in messages])


@private_message_bp.route("/<user_id>", methods=["POST"])
@login_required()
def send_private_message(user_id):
    message = request.get_json().get("message")

    private_message = PrivateMessage(
        content=message,
        from_user_id=g.current_user.id,
        to_user_id=user_id,
    )

    db.session.add(private_message)
    db.session.commit()

    return jsonify({ "message": "Message envoyé." })
