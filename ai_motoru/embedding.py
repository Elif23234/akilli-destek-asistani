import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


PROJE_KLASORU = Path(__file__).resolve().parent.parent
ENV_DOSYASI = PROJE_KLASORU / ".env"

load_dotenv(ENV_DOSYASI)

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client

    api_anahtari = os.getenv("GEMINI_API_KEY")
    if not api_anahtari:
        raise RuntimeError(
            "GEMINI_API_KEY bulunamadı. Proje kökündeki .env dosyasını kontrol et."
        )

    _client = genai.Client(api_key=api_anahtari)
    return _client


def embedding_olustur(metin: str) -> list[float]:
    if not metin or not metin.strip():
        raise ValueError("Embedding oluşturulacak metin boş olamaz.")

    client = _get_client()
    cevap = client.models.embed_content(
        model="gemini-embedding-001",
        contents=metin.strip(),
        config=types.EmbedContentConfig(
            output_dimensionality=768
        ),
    )

    if not cevap.embeddings:
        raise RuntimeError("Gemini embedding sonucu döndürmedi.")

    return cevap.embeddings[0].values