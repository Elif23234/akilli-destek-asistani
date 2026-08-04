import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))


def eposta_gonder(
    alici_eposta: str,
    konu: str,
    mesaj: str,
):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_EMAIL veya SMTP_PASSWORD .env dosyasında tanımlı değil."
        )

    eposta = MIMEMultipart()

    eposta["From"] = SMTP_EMAIL
    eposta["To"] = alici_eposta
    eposta["Subject"] = konu

    eposta.attach(
        MIMEText(
            mesaj,
            "plain",
            "utf-8",
        )
    )

    with smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT,
        timeout=30,
    ) as smtp:

        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(
            SMTP_EMAIL,
            SMTP_PASSWORD,
        )

        smtp.send_message(eposta)