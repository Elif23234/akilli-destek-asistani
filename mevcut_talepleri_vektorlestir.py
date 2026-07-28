import psycopg2

from ai_motoru.embedding import embedding_olustur


DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "destek_sistemi",
    "user": "postgres",
    "password": "postgres"
}


def mevcut_talepleri_vektorlestir():
    conn = None
    cursor = None

    try:
        print("Veritabanına bağlanılıyor...")

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        talepleri_getir_sorgusu = """
            SELECT
                talep_id,
                talep_takip_no,
                talep_baslik,
                talep_ham_icerik
            FROM talepler
            ORDER BY talep_olusturulma_tarihi
        """

        cursor.execute(talepleri_getir_sorgusu)
        talepler = cursor.fetchall()

        print(f"Toplam {len(talepler)} talep bulundu.")

        eklenen_sayisi = 0
        atlanan_sayisi = 0
        hata_sayisi = 0

        for talep in talepler:
            talep_id = talep[0]
            takip_no = talep[1]
            baslik = talep[2] or ""
            icerik = talep[3] or ""

            kontrol_sorgusu = """
                SELECT COUNT(*)
                FROM talep_vektorleri
                WHERE vektor_talep_id = %s
            """

            cursor.execute(kontrol_sorgusu, (talep_id,))
            mevcut_vektor_sayisi = cursor.fetchone()[0]

            if mevcut_vektor_sayisi > 0:
                print(f"Atlandı: {takip_no} için vektör zaten bulunuyor.")
                atlanan_sayisi = atlanan_sayisi + 1
                continue

            if baslik.strip() == "" and icerik.strip() == "":
                print(f"Atlandı: {takip_no} için başlık ve içerik boş.")
                atlanan_sayisi = atlanan_sayisi + 1
                continue

            vektor_metni = (
                f"Başlık: {baslik}\n"
                f"İçerik: {icerik}"
            )

            try:
                print(f"Vektör oluşturuluyor: {takip_no}")

                vektor_degerleri = embedding_olustur(vektor_metni)

                vektor_ekle_sorgusu = """
                    INSERT INTO talep_vektorleri
                    (
                        vektor_talep_id,
                        vektor_deger,
                        vektor_metin_parcasi
                    )
                    VALUES (%s, %s, %s)
                """

                cursor.execute(
                    vektor_ekle_sorgusu,
                    (
                        talep_id,
                        str(vektor_degerleri),
                        vektor_metni
                    )
                )

                conn.commit()

                eklenen_sayisi = eklenen_sayisi + 1
                print(f"Başarılı: {takip_no} kaydedildi.")

            except Exception as talep_hatasi:
                conn.rollback()

                hata_sayisi = hata_sayisi + 1
                print(f"Hata: {takip_no} vektörleştirilemedi.")
                print(talep_hatasi)

        print("\nİşlem tamamlandı.")
        print(f"Eklenen vektör: {eklenen_sayisi}")
        print(f"Atlanan talep: {atlanan_sayisi}")
        print(f"Hatalı talep: {hata_sayisi}")

    except Exception as genel_hata:
        if conn:
            conn.rollback()

        print("Kritik hata oluştu:")
        print(genel_hata)

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

        print("Veritabanı bağlantısı kapatıldı.")


if __name__ == "__main__":
    mevcut_talepleri_vektorlestir()