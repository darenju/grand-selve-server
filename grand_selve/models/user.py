from sqlalchemy import or_, Enum as SQLAEnum, func
from enum import Enum

from .private_message import PrivateMessage
from ..extensions import db


class UserRoleEnum(Enum):
  ADMIN = "admin"
  USER = "user"


class User(db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True, nullable=False)
  avatar_path = db.Column(db.String(300), nullable=True, default="")
  password_hash = db.Column(db.String(200), nullable=False)
  changed_first_password = db.Column(db.Boolean, nullable=False, default=False)
  first_name = db.Column(db.String(100), nullable=True, default="")
  last_name = db.Column(db.String(100), nullable=True, default="")
  name = db.column_property(first_name + " " + last_name)
  gender = db.Column(db.String(6), nullable=True, default="")
  date_of_birth = db.Column(db.Date, nullable=True)

  telephone = db.Column(db.String(14), nullable=True, default="")
  address = db.Column(db.String(200), nullable=True, default="")
  zipcode = db.Column(db.String(10), nullable=True, default="")
  city = db.Column(db.String(100), nullable=True, default="")
  
  baptism = db.Column(db.Date, nullable=True)
  confirmation = db.Column(db.Date, nullable=True)
  first_communion = db.Column(db.Date, nullable=True)
  marriage = db.Column(db.Date, nullable=True)
  ordination = db.Column(db.Date, nullable=True)

  service_links = db.relationship("UserServiceRole", back_populates="user")
  forum_messages = db.relationship("ForumMessage", back_populates="user")

  role = db.Column(SQLAEnum(UserRoleEnum), nullable=False)

  def to_dict(self, detailed=False):
    result = {
      "id": self.id,
      "email": self.email,
      "avatar_path": self.avatar_path,
      "changed_first_password": self.changed_first_password,
      "first_name": self.first_name,
      "last_name": self.last_name,
      "name": self.name,
      "gender": self.gender,
      "date_of_birth":  self.date_of_birth.strftime("%Y-%m-%d") if self.date_of_birth is not None else "",
      
      "telephone": self.telephone,
      "address": self.address,
      "zipcode": self.zipcode,
      "city": self.city,
      
      "baptism":  self.baptism.strftime("%Y-%m-%d") if self.baptism is not None else "",
      "confirmation":  self.confirmation.strftime("%Y-%m-%d") if self.confirmation is not None else "",
      "first_communion":  self.first_communion.strftime("%Y-%m-%d") if self.first_communion is not None else '',
      "marriage": self.marriage.strftime("%Y-%m-%d") if self.marriage is not None else '',
      "ordination": self.ordination.strftime("%Y-%m-%d") if self.ordination is not None else '',

      "role": self.role.value,
    }

    if detailed:
      result["services"] = [s.to_dict_service() for s in self.service_links]
    
    return result

  def private_messages_count(self):
    print(self.id)
    return db.session.query(func.count(PrivateMessage.id)).filter_by(to_user_id=self.id, read=False).scalar()

def filter_users(filters):
  or_filters = []

  if "email" in filters or "*" in filters:
    or_filters.append(User.email.ilike(f'%{filters.get("email") or filters.get("*")}%'))

  if "first_name" in filters or "*" in filters:
    or_filters.append(User.first_name.ilike(f'%{filters.get("first_name") or filters.get("*")}%'))
  
  if "last_name" in filters or "*" in filters:
    or_filters.append(User.last_name.ilike(f'%{filters.get("last_name") or filters.get("*")}%'))

  if filters.get("name") or filters.get("*"):
    or_filters.append(User.name.ilike(f'%{filters.get("name") or filters.get("*")}%'))

  return db.session.query(User).filter(or_(*or_filters)).all()
