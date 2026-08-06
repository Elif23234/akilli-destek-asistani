import sys
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import text

# Proje kök dizinini Python arama yoluna otomatik ekler
PROJE_KOK = Path(__file__).resolve().parents[1] 

if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

from ai_motoru.models import AnalizIstegi
from ai_motoru.pipeline import talebi_analiz_et
from database import SessionLocal
from eposta_service import eposta_gonder
from services import (
    bildirim_hash_olustur,
    kategori_id_bul,
    telegram_mesaji_gonder,
)

RISKLI_KATEGORILER: List[int] = [1, 3, 4, 7, 8]


def en_az_yuku_olan_personeli_bul(
    db: Session,
    departman: str,
):
    sorgu = text("""
        SELECT
            k.kullanici_id
        FROM kullanicilar k

        LEFT JOIN talepler t
            ON t.talep_atanan_personel_id =
               k.kullanici_id
           AND LOWER(TRIM(t.talep_durum))
               NOT IN (
                   'cozuldu',
                   'kapali'
               )

        WHERE LOWER(TRIM(k.kullanici_rol)) =
              'personel'

          AND LOWER(
              TRIM(k.kullanici_departman)
          ) = LOWER(
              TRIM(:departman)
          )

          AND LOWER(
              TRIM(k.kullanici_ad_soyad)
          ) <> 'sistem personeli'

        GROUP BY
            k.kullanici_id,
            k.kullanici_olusturulma_tarihi

        ORDER BY
            COUNT(t.talep_id) ASC,
            k.kullanici_olusturulma_tarihi ASC

        LIMIT 1;
    """)

    personel_id = db.execute(
        sorgu,
        {
            "departman": departman,
        },
    ).scalar()

    if personel_id:
        return personel_id

    genel_destek_sorgu = text("""
        SELECT
            k.kullanici_id
        FROM kullanicilar k

        LEFT JOIN talepler t
            ON t.talep_atanan_personel_id =
               k.kullanici_id
           AND LOWER(TRIM(t.talep_durum))
               NOT IN (
                   'cozuldu',
                   'kapali'
               )

        WHERE LOWER(TRIM(k.kullanici_rol)) =
              'personel'

          AND LOWER(
              TRIM(k.kullanici_departman)
          ) = 'genel destek'

          AND LOWER(
              TRIM(k.kullanici_ad_soyad)
          ) <> 'sistem personeli'

        GROUP BY
            k.kullanici_id,
            k.kullanici_olusturulma_tarihi

        ORDER BY
            COUNT(t.talep_id) ASC,
            k.kullanici_olusturulma_tarihi ASC

        LIMIT 1;
    """)

    return db.execute(
        genel_destek_sorgu
    ).scalar()
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


def ai_sonucu_isle(
    talep_id: str,
    baslik: str,
    icerik: str,
):
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
        oncelik_skoru = analiz_sonucu.oncelik_skoru
        oncelik_seviyesi = analiz_sonucu.oncelik_seviyesi
        duygu_durumu = analiz_sonucu.duygu_durumu
        oncelik_gerekcesi = analiz_sonucu.oncelik_gerekcesi
        guven_skoru = analiz_sonucu.guven_skoru
        cozum_onerisi = analiz_sonucu.cozum_onerisi
        onerilen_cevap = analiz_sonucu.onerilen_cevap

        # 3. Kategori adına göre ID'yi bul
        kategori_id = kategori_id_bul(
            db,
            kategori_adi,
        )

        # Kategorinin bağlı olduğu departmanı bul
        departman_sorgu = text("""
            SELECT kategori_departman
            FROM kategoriler
            WHERE kategori_id = :kategori_id;
        """)

        kategori_departman = db.execute(
            departman_sorgu,
            {
                "kategori_id": kategori_id,
            },
        ).scalar()

        if not kategori_departman:
            kategori_departman = "Genel Destek"

        # 4. Riskli kategori kontrolü ve etiketleme
        riskli_mi = (
            kategori_id in RISKLI_KATEGORILER
        )
        

        # --- HİBRİT YÖNLENDİRME MANTIĞI ---

        # Kritik talepler doğrudan personel incelemesine gider.
        if oncelik_seviyesi == "Kritik":
            yeni_durum = "inceleniyor"

        # Riskli kategoriler yönetici/personel onayı bekler.
        elif riskli_mi:
            yeni_durum = "onay_bekliyor"

        # Güven skoru düşükse personel inceler.
        elif guven_skoru < 0.80:
            yeni_durum = "inceleniyor"

        # Diğer güvenilir talepler otomatik yanıtlanır.
        else:
            yeni_durum = "otomatik_yanitlandi"

        if yeni_durum in (
            "inceleniyor",
            "onay_bekliyor",
        ):
            atanan_personel_id = (
                en_az_yuku_olan_personeli_bul(
                    db,
                    kategori_departman,
                )
            )
        else:
            atanan_personel_id = None

        print(
            "AI kategorisi:",
            kategori_adi,
        )

        print(
            "Kategori departmanı:",
            kategori_departman,
        )

        print(
            "Otomatik atanan personel ID:",
            atanan_personel_id,
        )
          
        print(">>> OTOMATİK YANIT BLOĞUNA GİRİLDİ <<<")
        if yeni_durum == "otomatik_yanitlandi":
            try:
                musteri_sorgu = text("""
                    SELECT
                        talep_gonderen_ad_soyad,
                        talep_gonderen_eposta,
                        talep_takip_no,
                        talep_baslik
                    FROM talepler
                    WHERE talep_id = :talep_id;
                """)

                musteri_sonucu = db.execute(
                    musteri_sorgu,
                    {
                        "talep_id": talep_id,
                    },
                ).first()

                if not musteri_sonucu:
                    raise RuntimeError(
                        "Otomatik yanıt gönderilecek talep bulunamadı."
                    )

                musteri_bilgisi = dict(
                    musteri_sonucu._mapping
                )

                musteri_eposta = (
                    musteri_bilgisi.get(
                        "talep_gonderen_eposta"
                    )
                    or ""
                ).strip()

                if not musteri_eposta:
                    raise RuntimeError(
                        "Talebe ait müşteri e-posta adresi bulunamadı."
                    )

                musteri_adi = (
                    musteri_bilgisi.get(
                        "talep_gonderen_ad_soyad"
                    )
                    or "Değerli Müşterimiz"
                )

                takip_no = (
                    musteri_bilgisi.get(
                        "talep_takip_no"
                    )
                    or "Belirtilmemiş"
                )

                talep_basligi = (
                    musteri_bilgisi.get(
                        "talep_baslik"
                    )
                    or baslik
                )

                cozuldu_linki = (
                    "http://localhost:5173/"
                    "musteri-onayi"
                    f"?talep_id={talep_id}"
                    "&sonuc=evet"
                )

                cozulmedi_linki = (
                    "http://localhost:5173/"
                    "musteri-onayi"
                    f"?talep_id={talep_id}"
                    "&sonuc=hayir"
                )

                eposta_konusu = (
                    "Destek Talebiniz Otomatik "
                    f"Yanıtlandı - {takip_no}"
                )

                eposta_mesaji = f"""Merhaba {musteri_adi},

"{talep_basligi}" başlıklı destek talebiniz yapay zekâ destekli sistemimiz tarafından değerlendirilmiştir.

Takip Numaranız: {takip_no}

Yapay Zekâ Yanıtı:
{onerilen_cevap}

Lütfen çözüm durumunu belirtin:

Sorunum çözüldü:
{cozuldu_linki}

Sorunum devam ediyor:
{cozulmedi_linki}

Bu yanıt yapay zekâ tarafından otomatik olarak oluşturulmuştur.

Saygılarımızla,
Akıllı Müşteri Destek Ekibi
"""

                eposta_gonder(
                    alici_eposta=musteri_eposta,
                    konu=eposta_konusu,
                    mesaj=eposta_mesaji,
                )

                print(
                    "Yapay zekâ otomatik e-postası "
                    f"gönderildi: {takip_no}"
                )

            except Exception as eposta_hatasi:
                   print("EPOSTA HATASI")
                   print(eposta_hatasi)

                   yeni_durum = "inceleniyor"


        # 5. Veritabanındaki ilgili talep kaydını ve YZ analizini güncelle/kaydet
        talep_sorgu = text("""
    UPDATE talepler
    SET
        talep_kategori_id = :kategori_id,
        talep_durum = :yeni_durum,
        talep_atanan_personel_id =
            :atanan_personel_id
    WHERE talep_id = :talep_id
""")
        print(
    "Otomatik atanan personel ID:",
    atanan_personel_id,
)
        db.execute(
    talep_sorgu,
    {
        "kategori_id": kategori_id,
        "yeni_durum": yeni_durum,
        "atanan_personel_id":
            atanan_personel_id,
        "talep_id": talep_id,
    },
)

        analiz_sorgu = text("""
            INSERT INTO yz_analizleri (
                yz_talep_id,
                yz_ozet,
                yz_oncelik_skoru,
                yz_oncelik_seviyesi,
                yz_duygu_durumu,
                yz_oncelik_gerekcesi,
                yz_guven_skoru,
                yz_cozum_onerisi,
                yz_musteri_cevabi
            )
            VALUES (
                :talep_id,
                :ozet,
                :oncelik_skoru,
                :oncelik_seviyesi,
                :duygu_durumu,
                :oncelik_gerekcesi,
                :guven_skoru,
                :cozum_onerisi,
                :onerilen_cevap
            )
            ON CONFLICT (yz_talep_id) DO UPDATE
            SET yz_ozet = EXCLUDED.yz_ozet,
                yz_oncelik_skoru = EXCLUDED.yz_oncelik_skoru,
                yz_oncelik_seviyesi = EXCLUDED.yz_oncelik_seviyesi,
                yz_duygu_durumu = EXCLUDED.yz_duygu_durumu,
                yz_oncelik_gerekcesi = EXCLUDED.yz_oncelik_gerekcesi,
                yz_guven_skoru = EXCLUDED.yz_guven_skoru,
                yz_cozum_onerisi = EXCLUDED.yz_cozum_onerisi,
                yz_musteri_cevabi = EXCLUDED.yz_musteri_cevabi
        """)

        db.execute(
            analiz_sorgu,
            {
                "talep_id": talep_id,
                "ozet": analiz_sonucu.ozet,
                "oncelik_skoru": oncelik_skoru,
                "oncelik_seviyesi": oncelik_seviyesi,
                "duygu_durumu": duygu_durumu,
                "oncelik_gerekcesi": oncelik_gerekcesi,
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
            try:
                bildirim_hash = bildirim_hash_olustur(talep_id)

                # Talebin takip numarasını ve bildirim durumunu getir.
                # FOR UPDATE, aynı talebin eş zamanlı olarak iki kez
                # bildirilmesini engellemeye yardımcı olur.
                bildirim_kontrol_sorgu = text("""
                    SELECT
                        talep_takip_no,
                        COALESCE(talep_bildirildi, FALSE)
                            AS talep_bildirildi
                    FROM talepler
                    WHERE talep_id = :talep_id
                    FOR UPDATE
                """)

                bildirim_kontrol = db.execute(
                    bildirim_kontrol_sorgu,
                    {"talep_id": talep_id},
                ).first()

                if bildirim_kontrol:
                    talep_takip_no = bildirim_kontrol.talep_takip_no
                    talep_bildirildi = bildirim_kontrol.talep_bildirildi

                    # Eski bildirim kayıtlarında hash var mı kontrol et.
                    hash_kontrol_sorgu = text("""
                        SELECT 1
                        FROM bildirim_kayitlari
                        WHERE bildirim_hash = :hash
                    """)

                    hash_kaydi_var = db.execute(
                        hash_kontrol_sorgu,
                        {"hash": bildirim_hash},
                    ).scalar()

                    if talep_bildirildi:
                        print(
                            "Telegram bildirimi daha önce gönderilmiş: "
                            f"{talep_takip_no}"
                        )

                    elif hash_kaydi_var:
                        # Eski sistemde bildirim gönderilmiş ancak
                        # talep_bildirildi alanı güncellenmemiş olabilir.
                        bildirildi_guncelle_sorgu = text("""
                            UPDATE talepler
                            SET talep_bildirildi = TRUE
                            WHERE talep_id = :talep_id
                        """)

                        db.execute(
                            bildirildi_guncelle_sorgu,
                            {"talep_id": talep_id},
                        )

                        print(
                            "Eski bildirim kaydı bulundu. "
                            "Tekrar Telegram mesajı gönderilmedi: "
                            f"{talep_takip_no}"
                        )

                    else:
                               basarili = telegram_mesaji_gonder(
                               talep_id=talep_id,
                               talep_takip_no=talep_takip_no,
                               baslik=baslik,
                               oncelik=oncelik_seviyesi,
                               kategori=kategori_adi,
                               duygu_durumu=duygu_durumu,
                               ai_ozeti=analiz_sonucu.ozet,
                                  )

                    if basarili:
                            # Telegram başarılıysa talebi bildirildi yap.
                            bildirildi_guncelle_sorgu = text("""
                                UPDATE talepler
                                SET talep_bildirildi = TRUE
                                WHERE talep_id = :talep_id
                            """)

                            db.execute(
                                bildirildi_guncelle_sorgu,
                                {"talep_id": talep_id},
                            )

                            # Bildirim geçmişini kaydet.
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

                            print(
                                "Telegram bildirimi gönderildi: "
                                f"{talep_takip_no}"
                            )

                    else:
                            print(
                                "Telegram bildirimi gönderilemedi. "
                                "talep_bildirildi değeri FALSE kaldı."
                            )

            except Exception as e:
                print(f"Telegram bildirimi hatası: {e}")
                # Kritik taleplerde sistem bilgilendirmesi ekle
        if oncelik_seviyesi == "Kritik":
            db.execute(
                yorum_sorgu,
                {
                    "talep_id": talep_id,
                    "yorum_mesaj": (
                        "[SİSTEM BİLDİRİMİ]: "
                        "Talebiniz yapay zekâ tarafından kritik öncelikli olarak "
                        "değerlendirilmiştir. Talebiniz ilgili destek personeline "
                        "yönlendirilmiş olup inceleme süreci başlatılmıştır."
                    ),
                },
            )

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
            "mesaj": (
                "YZ analizi başarıyla tamamlandı "
                "ve veritabanına işlendi."
            ),
            "kategori_id": kategori_id,
            "oncelik_skoru": oncelik_skoru,
            "oncelik_seviyesi": oncelik_seviyesi,
            "duygu_durumu": duygu_durumu,
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
                {
                    "talep_id": talep_id,
                },
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
    return ai_sonucu_isle(
        talep_id,
        baslik,
        icerik,
    )