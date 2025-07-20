from datetime import datetime
from ..extensions import db

class ForumMessage(db.Model):
  __tablename__ = 'forum_message'

  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.String(200), nullable=False)
  posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
  service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

  service = db.relationship("Service", back_populates="forum_messages")
  user = db.relationship("User", back_populates="forum_messages")

  def to_dict(self):
    return {
      "id": self.id,
      "message": self.message,
      "posted": self.posted.strftime("%Y-%m-%d %H:%M:%S"),
      "user": self.user.to_dict(),
    }
