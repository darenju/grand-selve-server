from setuptools import setup, find_packages

requires = (
  "psycopg2-binary",
  "flask",
  "flask_cors",
  "Flask-SQLAlchemy",
  "sqlalchemy",
  "Flask-Migrate",
  "werkzeug",
  "PyJWT",
)

setup(
  name="grand_selve",
  version="1.0",
  install_requires=requires,
  author="Julien Fradin",
  author_email="julien@frad.in",
  description=("L'application serveur pour la paroisse Grand Selve"),
  packages=["grand_selve"],
)
