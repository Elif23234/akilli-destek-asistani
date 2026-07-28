import sys
import argparse
from pathlib import Path

# Proje kök dizinini Python arama yoluna ekler
PROJE_KOK = Path(__file__).resolve().parents[1]

if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

from sqlalchemy import text

from database import SessionLocal
from ai_motoru.models import AnalizIstegi
from ai_motoru.pipeline import talebi_analiz_et
from services import kategori_id_bul


def analizsiz_talepleri_getir(db):
    sorgu = text("""
        SELECT
            t.talep_id,
            t.talep_takip_no,
            t.talep_baslik,
            t.talep_ham_icerik
        FROM talepler t
        LEFT JOIN yz_analizleri yz
            ON t.talep_id = yz.yz_talep_id
        WHERE t.talep_kategori_id IS NULL
          AND yz.yz_talep_id IS NULL
        ORDER BY t.talep_olusturulma_tarihi ASC;
    """)

    sonuc = db.execute(sorgu)

    return [dict(satir._mapping) for satir in sonuc]


def talebi_guvenli_analiz_et(talep):
    db = SessionLocal()

    try:
        istek_paketi = AnalizIstegi(
            talep_id=str(talep["talep_id"]),
            baslik=talep["talep_baslik"] or "",
            icerik=talep["talep_ham_icerik"] or "",
            benzer_talepler=[]
        )

        analiz_sonucu = talebi_analiz_et(istek_paketi)

        kategori_id = kategori_id_bul(
            db,
            analiz_sonucu.kategori_adi
        )

        if kategori_id is None:
            raise ValueError(
                "AI tarafından belirlenen kategori "
                f"veritabanında bulunamadı: "
                f"{analiz_sonucu.kategori_adi}"
            )

        kategori_guncelleme_sorgusu = text("""
            UPDATE talepler
            SET talep_kategori_id = :kategori_id
            WHERE talep_id = :talep_id
              AND talep_kategori_id IS NULL;
        """)

        db.execute(
            kategori_guncelleme_sorgusu,
            {
                "kategori_id": kategori_id,
                "talep_id": talep["talep_id"]
            }
        )

        analiz_kaydetme_sorgusu = text("""
            INSERT INTO yz_analizleri (
                yz_talep_id,
                yz_ozet,
                yz_guven_skoru,
                yz_cozum_onerisi,
                yz_musteri_cevabi
            )
            VALUES (
                :talep_id,
                :ozet,
                :guven_skoru,
                :cozum_onerisi,
                :onerilen_cevap
            )
            ON CONFLICT (yz_talep_id) DO NOTHING;
        """)

        db.execute(
            analiz_kaydetme_sorgusu,
            {
                "talep_id": talep["talep_id"],
                "ozet": analiz_sonucu.ozet,
                "guven_skoru": analiz_sonucu.guven_skoru,
                "cozum_onerisi": analiz_sonucu.cozum_onerisi,
                "onerilen_cevap": analiz_sonucu.onerilen_cevap
            }
        )

        db.commit()

        return {
            "basarili": True,
            "kategori": analiz_sonucu.kategori_adi
        }

    except Exception as hata:
        db.rollback()

        return {
            "basarili": False,
            "hata": str(hata)
        }

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Eski ve analizsiz talepleri güvenli biçimde "
            "AI analizinden geçirir."
        )
    )

    parser.add_argument(
        "--uygula",
        action="store_true",
        help="Analiz sonuçlarını veritabanına kaydeder."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="İşlenecek en fazla talep sayısı."
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        talepler = analizsiz_talepleri_getir(db)
    finally:
        db.close()

    if args.limit is not None:
        talepler = talepler[:args.limit]

    print()
    print(f"Bulunan analizsiz talep sayısı: {len(talepler)}")

    if len(talepler) == 0:
        print("İşlenecek talep bulunamadı.")
        return

    if not args.uygula:
        print()
        print("ÖN İZLEME MODU")
        print("Veritabanında hiçbir değişiklik yapılmadı.")
        print()

        for talep in talepler:
            print(
                f"- {talep['talep_takip_no']} | "
                f"{talep['talep_baslik']}"
            )

        print()
        print("Gerçek işlemi başlatmak için şu komutu kullan:")
        print("python eski_talepleri_analiz_et.py --uygula")
        return

    basarili_sayi = 0
    hatali_sayi = 0

    print()
    print("AI analiz işlemi başladı...")
    print()

    for sira, talep in enumerate(talepler, start=1):
        takip_no = talep["talep_takip_no"]

        print(
            f"[{sira}/{len(talepler)}] "
            f"{takip_no} analiz ediliyor..."
        )

        sonuc = talebi_guvenli_analiz_et(talep)

        if sonuc["basarili"]:
            basarili_sayi = basarili_sayi + 1

            print(
                f"Başarılı | Kategori: "
                f"{sonuc['kategori']}"
            )
        else:
            hatali_sayi = hatali_sayi + 1

            print(
                f"Hata | {sonuc['hata']}"
            )

    print()
    print("İşlem tamamlandı.")
    print(f"Başarılı: {basarili_sayi}")
    print(f"Hatalı: {hatali_sayi}")


if __name__ == "__main__":
    main()