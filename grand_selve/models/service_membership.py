from datetime import datetime
from ..extensions import db

class Membership(db.Model):
    __tablename__ = "membership"

    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), primary_key=True)
    invited_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    joined = db.Column(db.DateTime, nullable=False, default=datetime.now)
    left = db.Column(db.DateTime, nullable=True)

    member = db.relationship("Member", back_populates="memberships")
    service = db.relationship("Service", back_populates="memberships")
    invited_by = db.relationship("User")

    def to_dict(self):
        return {
            "service": self.service.to_dict(),
            "invited_by": self.invited_by.to_dict(),
            "active": self.left is None,
        }

    def to_dict_member(self):
        return {
            "member": self.member.to_dict(),
            "joined": self.joined,
            "active": self.left is None,
            "left": self.left,
        }
