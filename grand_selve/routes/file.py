import os
from mimetypes import guess_type
from datetime import datetime
from flask import Blueprint, jsonify, request, g, current_app, send_file
from sqlalchemy import or_
from uuid import uuid4
from werkzeug.utils import secure_filename
from ..models.stored_file import StoredFile
from ..extensions import db, get_extension
from ..auth import login_required

file_bp = Blueprint("file", __name__, url_prefix="/files")


@file_bp.route("", methods=["GET"])
@login_required()
def get_files():
    filters = []

    if request.args.get("member_id"):
        filters.append(StoredFile.member_id == int(request.args.get("member_id")))

    if request.args.get("service_id"):
        filters.append(StoredFile.service_id == int(request.args.get("service_id")))

    files = db.paginate(db.select(StoredFile).filter(or_(*filters)))

    return {
        "files": [m.to_dict() for m in files.items],
        "pagination": list(files.iter_pages()),
    }


@file_bp.route("/<file_id>", methods=["GET"])
@login_required()
def get_file(file_id):
    file = StoredFile.query.get(int(file_id))

    if file is None:
        return jsonify({"message": "Fichier introuvable."}), 404

    path = file.path
    mimetype, _ = guess_type(path)

    return send_file(path, mimetype=mimetype)


@file_bp.route("", methods=["POST"])
@login_required()
def upload_file():
    for file in request.files.getlist("files"):
        original_filename = file.filename
        filename = secure_filename(f"{uuid4().hex}.{get_extension(original_filename)}")
        path = os.path.abspath(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        file.save(path)

        stored_file = StoredFile(
            name=original_filename,
            path=path,
            uploaded_at=datetime.now(),
            user_id=g.current_user.id,
        )

        if request.args.get("member_id"):
            stored_file.member_id = int(request.args.get("member_id"))

        if request.args.get("service_id"):
            stored_file.service_id = int(request.args.get("service_id"))

        db.session.add(stored_file)
        db.session.commit()

    return jsonify({ "message": "OK" })


@file_bp.route("/<file_id>", methods=["DELETE"])
@login_required()
def delete_file(file_id):
    file = StoredFile.query.get(int(file_id))

    if file is None:
        return jsonify({ "message": "Fichier introuvable." }), 404

    if file.user_id != g.current_user.id:
        return jsonify({ "message": "Vous n'avez pas la permission de supprimer ce fichier." }), 403


    os.unlink(file.path)

    db.session.delete(file)
    db.session.commit()

    return jsonify({ "message": "OK" })
