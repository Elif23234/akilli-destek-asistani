# services.py
from sqlalchemy import text
from sqlalchemy.orm import Session

def kategori_id_bul(db: Session, kategori_adi: str) -> int:
    """
    Yapay zekadan gelen metinsel kategori adını veritabanındaki ID'si ile eşleştirir.
    Eğer eşleşen kategori bulunamazsa sistemin çökmemesini önlemek için 
    varsayılan bir kategori ID (Örn: 1) döndürür.
    """
    sorgu = text("SELECT kategori_id FROM kategoriler WHERE kategori_ad = :k_adi")
    sonuc = db.execute(sorgu, {"k_adi": kategori_adi}).scalar()
    
    if sonuc:
        return sonuc
    
    # Eşleşme yoksa default/diğer kategori ID'si (örneğin 1) dönülür
    return 1