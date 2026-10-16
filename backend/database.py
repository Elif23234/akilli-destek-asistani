
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Render'da DATABASE_URL, yerelde ise varsayılan bağlantı kullanılır.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/destek_sistemi"
)

# Render bağlantısı SSL ister.
if "dpg-" in SQLALCHEMY_DATABASE_URL and "sslmode=" not in SQLALCHEMY_DATABASE_URL:
    separator = "&" if "?" in SQLALCHEMY_DATABASE_URL else "?"
    SQLALCHEMY_DATABASE_URL += f"{separator}sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
