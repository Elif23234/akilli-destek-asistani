from pydantic import BaseModel


class AdminGiris(BaseModel):
    kullanici_adi: str
    sifre: str


class PersonelGiris(BaseModel):
    eposta: str
    sifre: str