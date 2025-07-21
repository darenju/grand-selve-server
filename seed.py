import os
from grand_selve import create_app
from grand_selve.extensions import db
from grand_selve.models.user import User
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
  app = create_app()

  with app.app_context():
    if not User.query.filter_by(email="julien@frad.in").first():
      admin = User(
        email="julien@frad.in",
        password_hash=generate_password_hash(os.getenv("ADMIN_PASSWORD")),
        first_name="Julien",
        last_name="Fradin",
        gender="male",
      )
      db.session.add(admin)
      db.session.commit()
      print("✅ Admin user created.")
    else:
      print("ℹ️ Admin user already exists.")
