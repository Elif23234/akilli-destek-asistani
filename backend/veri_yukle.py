import os
import pandas as pd
import psycopg2
import uuid
import hashlib
import random
from psycopg2.extras import execute_values

# Projendeki embedding modülünü içe aktarıyoruz
from ai_motoru.embedding import embedding_olustur

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "destek_sistemi",
    "user": "postgres",
    "password": "postgres"
}

def rastgele_hash_uret(metin):
    """Benzersiz bir takip numarası (hash) üretir."""
    benzersiz_id = str(uuid.uuid4()) + metin
    hash_obj = hashlib.sha256(benzersiz_id.encode())
    return "TKT-" + hash_obj.hexdigest()[:8].upper()

def verileri_aktar():
    print("🚀 Veritabanına bağlanılıyor...")
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("📂 CSV dosyası okunuyor...")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_yolu = os.path.join(base_dir, "veri_seti", "Tickets.csv")
        
        df = pd.read_csv(csv_yolu)
        df = df.fillna("Belirtilmemiş")

        print("⏳ Veriler işleniyor, Hash kodları ve Vektörler (Embedding) oluşturuluyor...")
        
        basarili_kayit = 0

        for index, row in df.iterrows():
            # 1. Takip numarası için rastgele Hash kodu oluştur
            takip_hash = rastgele_hash_uret(row['talep_gonderen_eposta'])
            
            # Kategorilerin dağılımı için 1 ile 8 arası rastgele bir kategori ID atıyoruz
            # (Veritabanındaki seed datamıza uygun olarak)
            kategori_id = random.randint(1, 8)

            # 2. Talebi veritabanına ekle ve oluşan UUID'yi (talep_id) geri al
            insert_talep_query = """
                INSERT INTO talepler (
                    talep_takip_no, talep_baslik, talep_ham_icerik, talep_durum, 
                    talep_kaynak, talep_gonderen_ad_soyad, talep_gonderen_eposta, 
                    talep_olusturulma_tarihi, talep_kategori_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING talep_id
            """
            
            cursor.execute(insert_talep_query, (
                takip_hash,
                row['talep_baslik'],
                row['talep_ham_icerik'],
                row['talep_durum'],
                row['talep_kaynak'],
                row['talep_gonderen_ad_soyad'],
                row['talep_gonderen_eposta'],
                row['talep_olusturulma_tarihi'],
                kategori_id
            ))
            
            yeni_talep_id = cursor.fetchone()[0]

            # 3. Yorumlar tablosuna Çözüm Metnini ekle (Geçmiş personel yanıtı olarak)
            if row['cozum_metni'] != "Belirtilmemiş" and row['cozum_metni'].strip() != "":
                insert_yorum_query = """
                    INSERT INTO yorumlar (yorum_talep_id, yorum_mesaj)
                    VALUES (%s, %s)
                """
                cursor.execute(insert_yorum_query, (yeni_talep_id, row['cozum_metni']))

            # 4. Gemini API ile Embedding (Vektör) oluştur
            vektor_metni = f"Başlık: {row['talep_baslik']} İçerik: {row['talep_ham_icerik']} Çözüm: {row['cozum_metni']}"
            
            try:
                # Gemini embedding oluşturuyor
                vektor_degerleri = embedding_olustur(vektor_metni)
                
                # 5. Vektörü veritabanına pgvector formatında kaydet
                insert_vektor_query = """
                    INSERT INTO talep_vektorleri (vektor_talep_id, vektor_deger, vektor_metin_parcasi)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_vektor_query, (yeni_talep_id, str(vektor_degerleri), vektor_metni))
                
                basarili_kayit += 1
                print(f"✅ {takip_hash} başarıyla vektörleştirildi ve kaydedildi.")
                
            except Exception as e:
                print(f"⚠️ {takip_hash} vektörleştirilirken hata: {str(e)}")

        conn.commit()
        print(f"🎉 Mükemmel! Toplam {basarili_kayit} bilet, hash kodları ve vektörleriyle veritabanına aktarıldı.")

    except Exception as e:
        print(f"❌ Kritik bir hata oluştu: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("🔒 Veritabanı bağlantısı güvenle kapatıldı.")

if __name__ == "__main__":
    verileri_aktar()