from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL bağlantı adresi (Kullanıcı: postgres, Şifre: postgres, DB: destek_sistemi)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/destek_sistemi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()