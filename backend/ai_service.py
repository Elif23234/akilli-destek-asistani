import sys
from pathlib import Path
from typing import List

from sqlalchemy import text

# Proje kök dizinini Python arama yoluna otomatik ekler
PROJE_KOK = Path(__file__).resolve().parents[1]

if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

from ai_motoru.models import AnalizIstegi
from ai_motoru.pipeline import talebi_analiz_et
from database import SessionLocal
from services import (
    bildirim_hash_olustur,
    kategori_id_bul,
    telegram_mesaji_gonder,
)

RISKLI_KATEGORILER: List[int] = [1, 3, 4, 7, 8]


# Tekrar eden talep kontrolü
def tekrar_eden_talep_kontrol(
    db,
    eposta: str,
    baslik: str,
    icerik: str,
) -> bool:
    """
    Aynı kullanıcının (eposta), aynı başlık ve içerikle,
    son 24 saat içinde mükerrer talep açıp açmadığını kontrol eder.
    """
    sorgu = text("""
        SELECT COUNT(talep_id)
        FROM talepler
        WHERE talep_gonderen_eposta = :eposta
          AND talep_baslik = :baslik
          AND talep_ham_icerik = :icerik
          AND talep_olusturulma_tarihi >= NOW() - INTERVAL '24 hours'
    """)

    sonuc = db.execute(
        sorgu,
        {
            "eposta": eposta,
            "baslik": baslik,
            "icerik": icerik,
        },
    ).scalar()

    return sonuc > 0


def ai_sonucu_isle(talep_id: str, baslik: str, icerik: str):
    """
    Yapay zeka motorunu arka planda bağımsız bir veritabanı oturumuyla çalıştırır
    ve otomasyon kurallarını tetikler.
    """
    db = SessionLocal()

    try:
        # 1. Gelen verileri pipeline'ın beklediği Pydantic modeline otomatik paketle
        istek_paketi = AnalizIstegi(
            talep_id=talep_id,
            baslik=baslik,
            icerik=icerik,
            benzer_talepler=[],
        )

        # 2. Pipeline üzerinden otomatik analizi gerçekleştir
        analiz_sonucu = talebi_analiz_et(istek_paketi)

        kategori_adi = analiz_sonucu.kategori_adi
        oncelik_seviyesi = analiz_sonucu.oncelik_seviyesi
        guven_skoru = analiz_sonucu.guven_skoru
        cozum_onerisi = analiz_sonucu.cozum_onerisi
        onerilen_cevap = analiz_sonucu.onerilen_cevap

        # 3. Kategori adına göre ID'yi bul
        kategori_id = kategori_id_bul(db, kategori_adi)

        # 4. Riskli kategori kontrolü ve etiketleme
        riskli_mi = kategori_id in RISKLI_KATEGORILER

        # --- HİBRİT YÖNLENDİRME MANTIĞI ---
        if riskli_mi or oncelik_seviyesi == "Kritik":
            yeni_durum = "onay_bekliyor"
        elif guven_skoru < 0.80:
            yeni_durum = "inceleniyor"
        else:
            yeni_durum = "otomatik_yanitlandi"

        # 5. Veritabanındaki ilgili talep kaydını ve YZ analizini güncelle/kaydet
        talep_sorgu = text("""
            UPDATE talepler
            SET talep_kategori_id = :kategori_id,
                talep_durum = :yeni_durum
            WHERE talep_id = :talep_id
        """)

        db.execute(
            talep_sorgu,
            {
                "kategori_id": kategori_id,
                "yeni_durum": yeni_durum,
                "talep_id": talep_id,
            },
        )

        analiz_sorgu = text("""
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
            ON CONFLICT (yz_talep_id) DO UPDATE
            SET yz_ozet = EXCLUDED.yz_ozet,
                yz_guven_skoru = EXCLUDED.yz_guven_skoru,
                yz_cozum_onerisi = EXCLUDED.yz_cozum_onerisi,
                yz_musteri_cevabi = EXCLUDED.yz_musteri_cevabi
        """)

        db.execute(
            analiz_sorgu,
            {
                "talep_id": talep_id,
                "ozet": analiz_sonucu.ozet,
                "guven_skoru": guven_skoru,
                "cozum_onerisi": cozum_onerisi,
                "onerilen_cevap": onerilen_cevap,
            },
        )

        # 6. YZ'nin ürettiği yanıtı 'yorumlar' tablosuna otomatik ekle
        yorum_sorgu = text("""
            INSERT INTO yorumlar (
                yorum_talep_id,
                yorum_mesaj
            )
            VALUES (
                :talep_id,
                :yorum_mesaj
            )
        """)

        # Kritik talepler için Telegram bildirimi
        if oncelik_seviyesi == "Kritik":
            bildirim_hash = bildirim_hash_olustur(talep_id)

            kontrol_sorgu = text("""
                SELECT 1
                FROM bildirim_kayitlari
                WHERE bildirim_hash = :hash
            """)

            daha_once_gonderildi = db.execute(
                kontrol_sorgu,
                {"hash": bildirim_hash},
            ).scalar()

            if not daha_once_gonderildi:
                try:
                    takip_no_sorgu = text("""
                        SELECT talep_takip_no
                        FROM talepler
                        WHERE talep_id = :talep_id
                    """)

                    talep_takip_no = db.execute(
                        takip_no_sorgu,
                        {"talep_id": talep_id},
                    ).scalar()

                    basarili = telegram_mesaji_gonder(
                        talep_id,
                        talep_takip_no,
                        baslik,
                        oncelik_seviyesi,
                    )

                    if basarili:
                        kayit_sorgu = text("""
                            INSERT INTO bildirim_kayitlari (
                                bildirim_talep_id,
                                bildirim_kanal,
                                bildirim_hash,
                                bildirim_durum
                            )
                            VALUES (
                                :talep_id,
                                'telegram',
                                :hash,
                                'gonderildi'
                            )
                        """)

                        db.execute(
                            kayit_sorgu,
                            {
                                "talep_id": talep_id,
                                "hash": bildirim_hash,
                            },
                        )

                except Exception as e:
                    print(f"Telegram bildirimi hatası: {e}")

        db.execute(
            yorum_sorgu,
            {
                "talep_id": talep_id,
                "yorum_mesaj": (
                    "[Yapay Zeka Asistanı Çözüm Önerisi]: "
                    f"{onerilen_cevap}"
                ),
            },
        )

        db.commit()

        return {
            "mesaj": "YZ analizi başarıyla tamamlandı ve veritabanına işlendi.",
            "kategori_id": kategori_id,
            "guven_skoru": guven_skoru,
            "cozum_onerisi": cozum_onerisi,
            "onerilen_cevap": onerilen_cevap,
        }

    except Exception as e:
        db.rollback()
        print(f"Arka plan analiz hatası: {str(e)}")

        # Hata durumunda talebin askıda kalmaması için güvenli duruma alalım
        try:
            hata_sorgu = text("""
                UPDATE talepler
                SET talep_durum = 'inceleniyor'
                WHERE talep_id = :talep_id
            """)

            db.execute(
                hata_sorgu,
                {"talep_id": talep_id},
            )

            # Hatayı yorumlara da ekleyelim ki personel bilsin
            hata_yorum = text("""
                INSERT INTO yorumlar (
                    yorum_talep_id,
                    yorum_mesaj
                )
                VALUES (
                    :talep_id,
                    :yorum_mesaj
                )
            """)

            db.execute(
                hata_yorum,
                {
                    "talep_id": talep_id,
                    "yorum_mesaj": (
                        "[SİSTEM UYARISI]: YZ analizi sırasında hata oluştu, "
                        "talep manuel incelemeye alındı. "
                        f"Hata: {str(e)}"
                    ),
                },
            )

            db.commit()

        except Exception as inner_e:
            db.rollback()
            print(f"Hata loglama başarısız: {str(inner_e)}")

    finally:
        db.close()


def talep_analiz_et_ve_uygula(
    talep_id: str,
    baslik: str,
    icerik: str,
):
    ai_sonucu_isle(talep_id, baslik, icerik)