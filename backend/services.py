from sqlalchemy import text
from sqlalchemy.orm import Session
import os
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

PANEL_URL = "http://localhost:5173"


def kategori_id_bul(db: Session, kategori_adi: str) -> int:
    """
    Yapay zekadan gelen kategori adını veritabanındaki ID ile eşleştirir.
    """
    sorgu = text(
        "SELECT kategori_id FROM kategoriler WHERE kategori_ad = :k_adi"
    )

    sonuc = db.execute(
        sorgu,
        {"k_adi": kategori_adi}
    ).scalar()

    if sonuc:
        return sonuc

    return 1


def telegram_mesaji_gonder(
    talep_id: str,
    talep_takip_no: str,
    baslik: str,
    oncelik: str
):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        return False

    panel_url = "http://localhost:5173"

    # Örneğin #4835 değerini URL için %234835 haline getirir
    takip_no_url = talep_takip_no.replace("#", "%23")

    talep_linki = f"{panel_url}/talep-detay/{takip_no_url}"

    mesaj = f"""
🚨 ACİL DESTEK TALEBİ

Takip No:
{talep_takip_no}

Talep ID:
{talep_id}

Başlık:
{baslik}

Öncelik:
{oncelik}

🔗 Talebi Aç:
{talep_linki}
"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": mesaj
            },
            timeout=10
        )

        return response.status_code == 200

    except Exception as e:
        print(f"Telegram gönderilemedi: {e}")
        return False

def bildirim_hash_olustur(talep_id: str):
    return hashlib.sha256(
        f"{talep_id}-telegram".encode()
    ).hexdigest()