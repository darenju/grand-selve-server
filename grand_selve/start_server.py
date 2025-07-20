from grand_selve import create_app
from flask_migrate import upgrade

app = create_app()

with app.app_context():
    upgrade()
