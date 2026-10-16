from fastapi import APIRouter, Depends, HTTPException

from schemas.auth import AdminGiris, PersonelGiris

from security import (
    admin_bilgilerini_dogrula,
    admin_token_olustur,
    admin_token_dogrula,
    personel_bilgilerini_dogrula,
    personel_token_olustur,
    personel_token_dogrula,
)


router = APIRouter()
@router.post("/admin/giris", tags=["Admin"])
def admin_girisi(giris: AdminGiris):

    giris_basarili = admin_bilgilerini_dogrula(
        giris.kullanici_adi,
        giris.sifre,
    )

    if not giris_basarili:
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı adı veya şifre hatalı.",
        )

    token = admin_token_olustur(
        giris.kullanici_adi
    )

    return {
        "mesaj": "Yönetici girişi başarılı.",
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/personel/giris", tags=["Personel"])
def personel_girisi(giris: PersonelGiris):

    personel = personel_bilgilerini_dogrula(
        giris.eposta,
        giris.sifre,
    )

    if not personel:
        raise HTTPException(
            status_code=401,
            detail="Personel e-posta adresi veya şifre hatalı.",
        )

    token = personel_token_olustur(
        personel
    )

    return {
        "mesaj": "Personel girişi başarılı.",
        "access_token": token,
        "token_type": "bearer",
        "personel": {
            "kullanici_id": personel["kullanici_id"],
            "kullanici_eposta": personel["kullanici_eposta"],
            "kullanici_ad_soyad": personel["kullanici_ad_soyad"],
            "rol": personel["rol"],
        },
    }

@router.get("/admin/token-kontrol", tags=["Admin"])
def admin_token_kontrol(
    admin: dict = Depends(admin_token_dogrula),
):

    return {
        "mesaj": "Yönetici tokenı geçerli.",
        "kullanici_adi": admin["kullanici_adi"],
        "kullanici_id": admin["kullanici_id"],
        "rol": admin["rol"],
    }

@router.get("/personel/token-kontrol", tags=["Personel"])
def personel_token_kontrol(
    personel: dict = Depends(personel_token_dogrula),
):

    return {
        "mesaj": "Personel tokenı geçerli.",
        "kullanici_id": personel["kullanici_id"],
        "kullanici_eposta": personel["kullanici_eposta"],
        "kullanici_ad_soyad": personel["kullanici_ad_soyad"],
        "rol": personel["rol"],
    }