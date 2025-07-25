from datetime import datetime
from ..extensions import db

class PrivateMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sent = db.Column(db.DateTime, default=datetime.now, nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)
    read_sender = db.Column(db.Boolean, default=True, nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    deleted_sender = db.Column(db.Boolean, default=False, nullable=False)
    deleted_recipient = db.Column(db.Boolean, default=False, nullable=False)

    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "sent": self.sent,
            "read": self.read,
            "read_sender": self.read_sender,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,

            "from": self.from_user.to_dict(),
            "to": self.to_user.to_dict(),
        }
