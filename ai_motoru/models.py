from typing import Optional
from pydantic import BaseModel, Field


class BenzerTalep(BaseModel):
    baslik: str
    icerik: str
    cozum: str


class AnalizIstegi(BaseModel):
    talep_id: str
    baslik: str
    icerik: str
    benzer_talepler: list[BenzerTalep] = Field(default_factory=list)


class AnalizSonucu(BaseModel):
    kategori_adi: str

    ozet: str

    oncelik_skoru: float = Field(
        ge=0,
        le=1
    )

    oncelik_seviyesi: str

    duygu_durumu: str

    oncelik_gerekcesi: str

    guven_skoru: float = Field(
        ge=0,
        le=1
    )

    cozum_onerisi: Optional[str] = None

    onerilen_cevap: Optional[str] = None