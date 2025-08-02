import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to):
    server = os.getenv("EMAIL_SERVER")
    port = int(os.getenv("EMAIL_PORT"))
    from_address = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Nouvelle prise de contact"
    message["From"] = from_address
    message["To"] = to

    text = "Bonjour, ceci est un test"
    html = "<html><body><p>Bonjour, Ceci est un <b>test</b>.</p></body></html>"

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP(server, port) as server:
        server.starttls()
        server.login(from_address, password)
        server.sendmail(from_address, to, message.as_string())
