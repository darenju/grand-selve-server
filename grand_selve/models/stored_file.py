from datetime import datetime
from ..extensions import db


class StoredFile(db.Model):
    __tablename__ = "stored_files"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User")

    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=True)
    service = db.relationship("Service")

    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=True)
    member = db.relationship("Member")

    def to_dict(self, relationship = None):
        ret = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "uploaded_at": self.uploaded_at,
            "user_id": self.user_id,
            "user": self.user.to_dict(),

            "service_id": self.service_id,
            "member_id": self.member_id,
        }

        if relationship == "service" and self.service_id:
            ret["service"] = self.service.to_dict()

        if relationship == "member" and self.member_id:
            ret["member"] = self.member.to_dict()

        return ret
