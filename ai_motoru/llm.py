import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from ai_motoru.models import AnalizSonucu
from ai_motoru.prompts import ANALIZ_SISTEM_PROMPTU


# Proje kökündeki .env dosyasının yolu
env_dosyasi = Path(__file__).resolve().parent.parent / ".env"

# .env dosyasını yükle
load_dotenv(env_dosyasi)


def gemini_client_olustur():
    """
    Gemini istemcisini yalnızca yapay zekâ analizi çağrıldığında oluşturur.

    Böylece API anahtarı olmayan bir bilgisayarda FastAPI tamamen çökmez.
    Sadece yapay zekâ endpointi çağrıldığında hata oluşur.
    """

    api_anahtari = os.getenv("GEMINI_API_KEY")

    if not api_anahtari:
        raise ValueError(
            "GEMINI_API_KEY bulunamadı. "
            "Proje kökündeki .env dosyasını kontrol et."
        )

    return genai.Client(api_key=api_anahtari)


def talebi_llm_ile_analiz_et(
    baslik: str,
    icerik: str,
    rag_baglami: str
) -> dict:
    """
    Destek talebini Gemini ile analiz eder ve doğrulanmış sözlük döndürür.
    """

    if not baslik or not baslik.strip():
        raise ValueError("Talep başlığı boş olamaz.")

    if not icerik or not icerik.strip():
        raise ValueError("Talep içeriği boş olamaz.")

    client = gemini_client_olustur()

    kullanici_promptu = f"""
{ANALIZ_SISTEM_PROMPTU}

Analiz edilecek destek talebi:

Başlık:
{baslik.strip()}

İçerik:
{icerik.strip()}

Geçmiş benzer talepler:
{rag_baglami}
"""

    try:
        cevap = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=kullanici_promptu,
            config={
                "response_mime_type": "application/json",
                "response_schema": AnalizSonucu
            }
        )

    except Exception as hata:
        raise RuntimeError(
            f"Gemini API isteği başarısız oldu: {str(hata)}"
        ) from hata

    if not cevap.text:
        raise ValueError("Gemini boş cevap döndürdü.")

    try:
        analiz_sonucu = json.loads(cevap.text)

    except json.JSONDecodeError as hata:
        raise ValueError(
            f"Gemini geçerli JSON döndürmedi: {cevap.text}"
        ) from hata

    dogrulanmis_sonuc = AnalizSonucu.model_validate(
        analiz_sonucu
    )

    return dogrulanmis_sonuc.model_dump()