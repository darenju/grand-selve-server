from datetime import datetime
from sqlalchemy import or_, and_, select, func
from sqlalchemy.ext.hybrid import hybrid_property
from ..extensions import db
from ..models.service_membership import Membership


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=True, default="") # Not unique because might be used as parents' email.
    first_name = db.Column(db.String(100), nullable=True, default="")
    last_name = db.Column(db.String(100), nullable=True, default="")
    name = db.column_property(first_name + " " + last_name)
    gender = db.Column(db.String(6), nullable=True, default="")
    date_of_birth = db.Column(db.Date, nullable=True)

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_by = db.relationship("User")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    notes = db.Column(db.Text, nullable=True, default="")

    telephone = db.Column(db.String(14), nullable=True, default="")
    address = db.Column(db.String(200), nullable=True, default="")
    zipcode = db.Column(db.String(10), nullable=True, default="")
    city = db.Column(db.String(100), nullable=True, default="")

    baptism = db.Column(db.Date, nullable=True)
    confirmation = db.Column(db.Date, nullable=True)
    first_communion = db.Column(db.Date, nullable=True)
    marriage = db.Column(db.Date, nullable=True)

    memberships = db.relationship("Membership", back_populates="member")
    from_contact_card = db.Column(db.Integer, db.ForeignKey("contact_card.id"), nullable=True)

    @hybrid_property
    def services(self):
        return len([m for m in self.memberships if m.left is None])

    @services.expression
    def services(self):
        return (
            select(func.count(Membership.member_id))
            .where(Membership.member_id == self.id) # type: ignore
            .where(Membership.left is None) # type: ignore
            .correlate(self)
            .as_scalar()
        )

    def to_dict(self, detailed=False):
        result = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "name": self.name,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth.strftime("%Y-%m-%d") if self.date_of_birth is not None else "",

            "notes": self.notes,

            "telephone": self.telephone,
            "address": self.address,
            "zipcode": self.zipcode,
            "city": self.city,

            "baptism": self.baptism.strftime("%Y-%m-%d") if self.baptism is not None else "",
            "confirmation": self.confirmation.strftime("%Y-%m-%d") if self.confirmation is not None else "",
            "first_communion": self.first_communion.strftime("%Y-%m-%d") if self.first_communion is not None else '',
            "marriage": self.marriage.strftime("%Y-%m-%d") if self.marriage is not None else '',

            "services": self.services,
        }

        if detailed:
            result["memberships"] = [s.to_dict() for s in self.memberships if s.left is None]
            result["previous_memberships"] = [s.to_dict() for s in self.memberships if s.left is not None]

        return result


def filter_members(filters):
    or_filters = []
    and_filters = []

    if "email" in filters or "*" in filters:
        or_filters.append(Member.email.ilike(f'%{filters.get("email") or filters.get("*")}%'))

    if "first_name" in filters or "*" in filters:
        or_filters.append(Member.first_name.ilike(f'%{filters.get("first_name") or filters.get("*")}%'))

    if "last_name" in filters or "*" in filters:
        or_filters.append(Member.last_name.ilike(f'%{filters.get("last_name") or filters.get("*")}%'))

    name_filter = filters.get("name") or filters.get("*")
    if name_filter:
        or_filters.append(
            func.unaccent(Member.name).ilike(func.unaccent(f'%{name_filter}%'))
        )

    if "baptism" in filters:
        and_filters.append(Member.baptism.isnot(None))

    if "confirmation" in filters:
        and_filters.append(Member.confirmation.isnot(None))

    if "first_communion" in filters:
        and_filters.append(Member.first_communion.isnot(None))

    if "marriage" in filters:
        and_filters.append(Member.marriage.isnot(None))

    order_by = getattr(Member, filters.get("sort_column"))
    order_by_type = str(order_by.type)

    if "VARCHAR" in order_by_type:
        order_by = db.collate(order_by, "ignore_accents")

    order_by = getattr(order_by, filters.get("sort_direction"))()

    return db.paginate(db.select(Member).filter(or_(*or_filters), and_(*and_filters)).order_by(order_by))
