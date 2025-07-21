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
