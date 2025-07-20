from setuptools import setup

requires = (
  "fpdf2",
  "python-barcode",
  "qrcode",
  "flask",
  "flask_cors",
)

setup(
  name="kompakt_fidelity",
  version="1.0",
  author="Julien Fradin",
  author_email="julien@frad.in",
  description=("Generate a PDF of fidelity cards for the Mudita Kompakt"),
)
