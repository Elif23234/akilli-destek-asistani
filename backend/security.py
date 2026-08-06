import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import text

from database import SessionLocal


load_dotenv()


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    "",
).strip()
ADMIN_KULLANICI_ID = os.getenv(
    "ADMIN_KULLANICI_ID",
    "",
).strip()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()

JWT_ALGORITHM = "HS256"
ADMIN_TOKEN_SURE_DAKIKA = int(
    os.getenv("ADMIN_TOKEN_SURE_DAKIKA", "60")
)


if not ADMIN_USERNAME:
    raise RuntimeError(
        ".env içinde ADMIN_USERNAME bulunamadı."
    )

if not ADMIN_PASSWORD_HASH:
    raise RuntimeError(
        ".env içinde ADMIN_PASSWORD_HASH bulunamadı."
    )

if not ADMIN_KULLANICI_ID:
    raise RuntimeError(
        ".env içinde ADMIN_KULLANICI_ID bulunamadı."
    )

try:
    UUID(ADMIN_KULLANICI_ID)
except ValueError as hata:
    raise RuntimeError(
        "ADMIN_KULLANICI_ID geçerli bir UUID olmalıdır."
    ) from hata

if not JWT_SECRET_KEY:
    raise RuntimeError(
        ".env içinde JWT_SECRET_KEY bulunamadı."
    )


password_hash = PasswordHash.recommended()

bearer_guvenligi = HTTPBearer(
    auto_error=False
)


def admin_bilgilerini_dogrula(
    kullanici_adi: str,
    sifre: str,
) -> bool:
    kullanici_adi_dogru = secrets.compare_digest(
        kullanici_adi,
        ADMIN_USERNAME,
    )

    try:
        sifre_dogru = password_hash.verify(
            sifre,
            ADMIN_PASSWORD_HASH,
        )
    except Exception:
        sifre_dogru = False

    return kullanici_adi_dogru and sifre_dogru


def admin_token_olustur(
    kullanici_adi: str,
) -> str:
    sona_erme_zamani = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ADMIN_TOKEN_SURE_DAKIKA
        )
    )

    token_verisi = {
        "sub": kullanici_adi,
        "rol": "admin",
        "kullanici_id": ADMIN_KULLANICI_ID,
        "exp": sona_erme_zamani,
    }

    return jwt.encode(
        token_verisi,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def admin_token_dogrula(
    kimlik: HTTPAuthorizationCredentials
    | None = Depends(bearer_guvenligi),
) -> dict:
    yetkisiz_hatasi = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Yönetici oturumu bulunamadı "
            "veya oturumun süresi doldu."
        ),
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    if kimlik is None:
        raise yetkisiz_hatasi

    if kimlik.scheme.lower() != "bearer":
        raise yetkisiz_hatasi

    try:
        token_verisi = jwt.decode(
            kimlik.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except InvalidTokenError:
        raise yetkisiz_hatasi

    kullanici_adi = token_verisi.get("sub")
    rol = token_verisi.get("rol")
    kullanici_id = token_verisi.get("kullanici_id")

    if kullanici_adi != ADMIN_USERNAME:
        raise yetkisiz_hatasi

    if rol != "admin":
        raise yetkisiz_hatasi

    if kullanici_id != ADMIN_KULLANICI_ID:
        raise yetkisiz_hatasi

    try:
        UUID(str(kullanici_id))
    except ValueError:
        raise yetkisiz_hatasi

    return {
        "kullanici_adi": kullanici_adi,
        "rol": rol,
        "kullanici_id": kullanici_id,
    }
def personel_bilgilerini_dogrula(
    eposta: str,
    sifre: str,
) -> dict | None:
    db = SessionLocal()

    try:
        sorgu = text("""
            SELECT
                kullanici_id,
                kullanici_eposta,
                kullanici_ad_soyad,
                kullanici_rol,
                kullanici_sifre_hash
            FROM kullanicilar
            WHERE LOWER(TRIM(kullanici_eposta))
                = LOWER(TRIM(:eposta))
              AND LOWER(TRIM(kullanici_rol))
                = 'personel'
            LIMIT 1;
        """)

        sonuc = db.execute(
            sorgu,
            {
                "eposta": eposta,
            },
        ).first()

        if not sonuc:
            return None

        personel = dict(
            sonuc._mapping
        )

        try:
            sifre_dogru = password_hash.verify(
                sifre,
                personel["kullanici_sifre_hash"],
            )
        except Exception:
            sifre_dogru = False

        if not sifre_dogru:
            return None

        return {
            "kullanici_id":
                str(personel["kullanici_id"]),
            "kullanici_eposta":
                personel["kullanici_eposta"],
            "kullanici_ad_soyad":
                personel["kullanici_ad_soyad"],
            "rol":
                personel["kullanici_rol"],
        }

    finally:
        db.close()


def personel_token_olustur(
    personel: dict,
) -> str:
    sona_erme_zamani = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ADMIN_TOKEN_SURE_DAKIKA
        )
    )

    token_verisi = {
        "sub": personel["kullanici_eposta"],
        "rol": "personel",
        "kullanici_id":
            personel["kullanici_id"],
        "ad_soyad":
            personel["kullanici_ad_soyad"],
        "exp": sona_erme_zamani,
    }

    return jwt.encode(
        token_verisi,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def personel_token_dogrula(
    kimlik: HTTPAuthorizationCredentials
    | None = Depends(bearer_guvenligi),
) -> dict:
    yetkisiz_hatasi = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Personel oturumu bulunamadı "
            "veya oturumun süresi doldu."
        ),
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if kimlik is None:
        raise yetkisiz_hatasi

    if kimlik.scheme.lower() != "bearer":
        raise yetkisiz_hatasi

    try:
        token_verisi = jwt.decode(
            kimlik.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except InvalidTokenError:
        raise yetkisiz_hatasi

    eposta = token_verisi.get("sub")
    rol = token_verisi.get("rol")
    kullanici_id = token_verisi.get(
        "kullanici_id"
    )
    ad_soyad = token_verisi.get(
        "ad_soyad"
    )

    if not eposta:
        raise yetkisiz_hatasi

    if rol != "personel":
        raise yetkisiz_hatasi

    try:
        UUID(str(kullanici_id))
    except (ValueError, TypeError):
        raise yetkisiz_hatasi

    return {
        "kullanici_eposta": eposta,
        "kullanici_ad_soyad": ad_soyad,
        "rol": rol,
        "kullanici_id": kullanici_id,
    }