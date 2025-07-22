from datetime import datetime
from ..extensions import db

class ContactCard(db.Model):
  __tablename__ = 'contact_card'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False)
  email = db.Column(db.String(255), nullable=False, unique=True)
  telephone = db.Column(db.String(255), nullable=False, unique=True)
  interest = db.Column(db.String(100), nullable=False)
  notes = db.Column(db.Text, nullable=True)
  created = db.Column(db.DateTime, nullable=False, default=datetime.now)

  handled = db.Column(db.DateTime, nullable=True)
  handled_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
  handled_by = db.relationship("User")

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "email": self.email,
      "telephone": self.telephone,
      "interest": self.interest,
      "notes": self.notes,
      "created": self.created.isoformat() if self.created else None,
      "handled": self.handled.isoformat() if self.handled else None,
      "handled_by_id": self.handled_by_id,
      "handled_by": self.handled_by.to_dict() if self.handled_by else None,
    }
