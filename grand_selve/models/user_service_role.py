from sqlalchemy import Enum as SQLAEnum
from enum import Enum
from ..extensions import db

class ServiceRoleEnum(Enum):
  SUPERVISOR = "supervisor"
  PARTICIPANT = "participant"

class UserServiceRole(db.Model):
  __tablename__ = "user_service_roles"

  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
  service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
  role = db.Column(SQLAEnum(ServiceRoleEnum), nullable=False)

  user = db.relationship("User", back_populates="service_links")
  service = db.relationship("Service", back_populates="user_links")

  def to_dict_user(self):
    return {
      "id": self.id,
      "user": self.user.to_dict(),
      "role": self.role.value,
    }
  
  def to_dict_service(self):
    return {
      "id": self.id,
      "service": self.service.to_dict(),
      "role": self.role.value,
    }