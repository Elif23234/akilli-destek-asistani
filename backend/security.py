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