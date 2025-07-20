from datetime import datetime
from sqlalchemy import or_
from ..extensions import db

class Service(db.Model):
  __tablename__ = 'services'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  description = db.Column(db.Text, nullable=True)
  color = db.Column(db.String(7), nullable=True, default='#bdc3c7')
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  user_links = db.relationship("UserServiceRole", back_populates="service")
  forum_messages = db.relationship("ForumMessage", back_populates="service")
  memberships = db.relationship("Membership", back_populates="service")

  def to_dict(self, detailed=False):
    result = {
      "id": self.id,
      "name": self.name,
      "description": self.description,
      "color": self.color,
      "created_at": self.created_at,
      "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at is not None else "",
    }
    
    if detailed:
      result["animators"] = [l.to_dict_user() for l in self.user_links]
      result["memberships"] = sorted(
        [m.to_dict_member() for m in self.memberships],
        key=lambda m: m["left"] is not None,
      )
    
    return result

def filter_services(filters):
  or_filters = []

  if "name" in filters or "*" in filters:
    or_filters.append(Service.name.ilike(f'%{filters.get("name") or filters.get("*")}%'))
  
  if "description" in filters or "*" in filters:
    or_filters.append(Service.description.ilike(f'%{filters.get("description") or filters.get("*")}%'))

  return db.session.query(Service).filter(or_(*or_filters)).all()
