from sqlalchemy import text
from sqlalchemy.orm import Session
import os
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

PANEL_URL = "http://localhost:5173"


def kategori_id_bul(
    db: Session,
    kategori_adi: str,
) -> int:
    """
    Yapay zekadan gelen kategori adını
    veritabanındaki ID ile eşleştirir.
    """
    sorgu = text(
        """
        SELECT kategori_id
        FROM kategoriler
        WHERE kategori_ad = :k_adi
        """
    )

    sonuc = db.execute(
        sorgu,
        {
            "k_adi": kategori_adi,
        },
    ).scalar()

    if sonuc:
        return sonuc

    return 1


def telegram_mesaji_gonder(
    talep_id: str,
    talep_takip_no: str,
    baslik: str,
    oncelik: str,
    kategori: str = "",
    duygu_durumu: str = "",
    ai_ozeti: str = "",
) -> bool:
    bot_token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )
    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID"
    )

    if not bot_token or not chat_id:
        print(
            "Telegram token veya chat ID bulunamadı."
        )
        return False

    temiz_takip_no = (
        talep_takip_no or "Belirtilmemiş"
    ).strip()

    temiz_baslik = (
        baslik or "Başlık bulunmuyor"
    ).strip()

    temiz_oncelik = (
        oncelik or "Belirtilmemiş"
    ).strip()

    temiz_kategori = (
        kategori or "Belirtilmemiş"
    ).strip()

    temiz_duygu = (
        duygu_durumu or "Belirtilmemiş"
    ).strip()

    temiz_ozet = (
        ai_ozeti or
        "Bu talep için AI özeti oluşturulmamış."
    ).strip()

    takip_no_url = temiz_takip_no.replace(
        "#",
        "%23",
    )

    talep_linki = (
        f"{PANEL_URL}/talep-detay/"
        f"{takip_no_url}"
    )

    oncelik_kucuk = (
        temiz_oncelik
        .lower()
        .replace("İ", "i")
    )

    if oncelik_kucuk in (
        "kritik",
        "acil",
    ):
        onerilen_islem = (
            "Talebin öncelikli olarak ele alınması "
            "gerekmektedir."
        )
    elif oncelik_kucuk in (
        "yüksek",
        "yuksek",
    ):
        onerilen_islem = (
            "Talep en kısa sürede "
            "değerlendirilmelidir."
        )
    else:
        onerilen_islem = (
            "Talep normal iş akışında "
            "değerlendirilebilir."
        )

    mesaj = f"""
🚨 ACİL DESTEK TALEBİ

📌 Takip No:
{temiz_takip_no}

📂 Kategori:
{temiz_kategori}

😠 Duygu Durumu:
{temiz_duygu}

📝 Başlık:
{temiz_baslik}

🔥 Öncelik:
{temiz_oncelik}

🤖 AI Özeti:
{temiz_ozet}

⚠️ Önerilen İşlem:
{onerilen_islem}

🔗 Talebi Aç:
{talep_linki}
""".strip()

    url = (
        "https://api.telegram.org/"
        f"bot{bot_token}/sendMessage"
    )

    try:
        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": mesaj,
            },
            timeout=10,
        )

        if response.status_code != 200:
            print(
                "Telegram bildirimi gönderilemedi. "
                f"Durum kodu: {response.status_code}"
            )
            print(
                f"Telegram cevabı: {response.text}"
            )
            return False

        return True

    except requests.RequestException as hata:
        print(
            "Telegram isteği sırasında hata oluştu: "
            f"{hata}"
        )
        return False

    except Exception as hata:
        print(
            "Telegram gönderilemedi: "
            f"{hata}"
        )
        return False


def bildirim_hash_olustur(
    talep_id: str,
) -> str:
    return hashlib.sha256(
        f"{talep_id}-telegram".encode()
    ).hexdigest()