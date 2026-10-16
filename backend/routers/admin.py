from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from database import SessionLocal
from security import admin_token_dogrula


router = APIRouter()

@router.get(
    "/admin/personeller",
    tags=["Admin"],
)
def admin_personelleri_getir(
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()

    try:
        sorgu = text("""
            SELECT
                kullanici_id,
                kullanici_ad_soyad,
                kullanici_eposta,
                kullanici_rol
            FROM kullanicilar
            WHERE LOWER(
                TRIM(kullanici_rol)
            ) = 'personel'
            ORDER BY kullanici_ad_soyad ASC;
        """)

        sonuc = db.execute(sorgu)

        personeller = [
            dict(satir._mapping)
            for satir in sonuc
        ]

        return {
            "mesaj": "Personeller başarıyla getirildi.",
            "veri": personeller,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Personeller alınırken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()