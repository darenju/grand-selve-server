from setuptools import setup, find_packages

requires = (
  "psycopg2-binary",
  "python-dotenv",
  "flask",
  "flask_cors",
  "Flask-SQLAlchemy",
  "sqlalchemy",
  "Flask-Migrate",
  "werkzeug",
  "PyJWT",
  "waitress",
  "Flask-Caching",
  "redis",
)

setup(
  name="grand_selve",
  version="1.0",
  install_requires=requires,
  author="Julien Fradin",
  author_email="julien@frad.in",
  description=("L'application serveur pour la paroisse Grand Selve"),
  packages=find_packages(include=["grand_selve", "grand_selve.*", "migrations", "migrations.*", "migrations.versions", "migrations.versions.*"]),
  include_package_data=True,
)
