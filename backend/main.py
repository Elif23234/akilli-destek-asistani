import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from database import SessionLocal
from sqlalchemy import text
from ai_service import talep_analiz_et_ve_uygula, tekrar_eden_talep_kontrol
from ai_motoru.embedding import embedding_olustur
from fastapi.middleware.cors import CORSMiddleware
from security import (
    admin_bilgilerini_dogrula,
    admin_token_olustur,
    admin_token_dogrula,
    personel_bilgilerini_dogrula,
    personel_sifresi_dogrula,
    personel_sifresi_hashle,
    personel_token_olustur,
    personel_token_dogrula,
)
from eposta_service import eposta_gonder
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")





app = FastAPI(title="Akıllı Destek Asistanı API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- VERİ KARŞILAMA MODELLERİ (Dışarıdan Gelen JSON Formatları) ---
class YeniTalep(BaseModel):
    ad_soyad: str
    eposta: str
    baslik: str
    icerik: str
    kaynak: str = "web"
class AdminGiris(BaseModel):
    kullanici_adi: str
    sifre: str
class PersonelGiris(BaseModel):
    eposta: str
    sifre: str
class YeniYorum(BaseModel):
    talep_id: str
    mesaj: str
    yeni_durum: Optional[str] = None
class DurumGuncelleme(BaseModel):
    takip_no: str
    yeni_durum: str


class MusteriCozumOnayi(BaseModel):
    talep_id: str
    cozuldu_mu: bool


class PersonelOnayIslemi(BaseModel):
    talep_id: str
    yanit_metni: str
    islem_tipi: str = "AI_YANITI_ONAYLANDI"

class TalepDevretmeIstegi(BaseModel):
    talep_id: str
    yeni_personel_id: str

class TalepYonlendirme(BaseModel):
    talep_id: str
    yeni_kategori_id: int
    mesaj: str = "Talep yanlış departmana geldiği için ilgili birime yönlendirildi."
class PersonelSifreDegistirme(BaseModel):
    mevcut_sifre: str
    yeni_sifre: str

# --- API UÇ NOKTALARI ---

# 1. Ana Sayfa Testi
@app.get("/")
def read_root():
    return {"mesaj": "Akıllı Destek Asistanı backend sistemi başarıyla çalışıyor!"}
@app.post("/admin/giris", tags=["Admin"])
def admin_girisi(giris: AdminGiris):
    giris_basarili = admin_bilgilerini_dogrula(
        giris.kullanici_adi,
        giris.sifre,
    )

    if not giris_basarili:
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı adı veya şifre hatalı.",
        )

    token = admin_token_olustur(
        giris.kullanici_adi
    )

    return {
        "mesaj": "Yönetici girişi başarılı.",
        "access_token": token,
        "token_type": "bearer",
    }


@app.post(
    "/personel/giris",
    tags=["Personel"],
)
def personel_girisi(
    giris: PersonelGiris,
):
    personel = personel_bilgilerini_dogrula(
        giris.eposta,
        giris.sifre,
    )

    if not personel:
        raise HTTPException(
            status_code=401,
            detail="Personel e-posta adresi veya şifre hatalı.",
        )

    token = personel_token_olustur(
        personel
    )

    return {
        "mesaj": "Personel girişi başarılı.",
        "access_token": token,
        "token_type": "bearer",
        "personel": {
            "kullanici_id":
                personel["kullanici_id"],
            "kullanici_eposta":
                personel["kullanici_eposta"],
            "kullanici_ad_soyad":
                personel["kullanici_ad_soyad"],
            "rol":
                personel["rol"],
        },
    }



@app.get("/admin/token-kontrol", tags=["Admin"])
def admin_token_kontrol(
    admin: dict = Depends(admin_token_dogrula),
):
    return {
        "mesaj": "Yönetici tokenı geçerli.",
        "kullanici_adi": admin["kullanici_adi"],
        "kullanici_id": admin["kullanici_id"],
        "rol": admin["rol"],
    }

@app.get(
    "/admin/personeller",
    tags=["Admin"],
)
def admin_personelleri_getir(
    _admin: dict = Depends(
        admin_token_dogrula
    ),
):
    db = SessionLocal()

    try:
        sorgu = text("""
            SELECT
                kullanici_id,
                kullanici_ad_soyad,
                kullanici_eposta,
                kullanici_rol
            FROM kullanicilar
            WHERE LOWER(
                TRIM(kullanici_rol)
            ) = 'personel'
            ORDER BY
                kullanici_ad_soyad ASC;
        """)

        sonuc = db.execute(sorgu)

        personeller = [
            dict(satir._mapping)
            for satir in sonuc
        ]

        return {
            "mesaj": "Personeller başarıyla getirildi.",
            "veri": personeller,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Personeller alınırken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()

@app.post(
    "/admin/talep-devret",
    tags=["Admin"],
)
def admin_talebi_devret(
    veri: TalepDevretmeIstegi,
    admin: dict = Depends(
        admin_token_dogrula
    ),
):
    db = SessionLocal()

    try:
        
        talep_sorgu = text("""
        SELECT
        t.talep_id,
        t.talep_takip_no,
        t.talep_durum,
        t.talep_atanan_personel_id,
        eski.kullanici_ad_soyad
            AS eski_personel_adi
           FROM talepler t

               LEFT JOIN kullanicilar eski
        ON eski.kullanici_id =
           t.talep_atanan_personel_id

                WHERE t.talep_id = :talep_id;
""")

        talep_sonucu = db.execute(
            talep_sorgu,
            {
                "talep_id": veri.talep_id,
            },
        ).first()

        if not talep_sonucu:
            raise HTTPException(
                status_code=404,
                detail="Talep bulunamadı.",
            )

        personel_sorgu = text("""
            SELECT
                kullanici_id,
                kullanici_ad_soyad
            FROM kullanicilar
            WHERE kullanici_id =
                  :personel_id
              AND LOWER(
                  TRIM(kullanici_rol)
              ) = 'personel';
        """)

        personel_sonucu = db.execute(
            personel_sorgu,
            {
                "personel_id":
                    veri.yeni_personel_id,
            },
        ).first()

        if not personel_sonucu:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Devredilecek yeni personel "
                    "bulunamadı."
                ),
            )

        talep = dict(
            talep_sonucu._mapping
        )
        if talep["talep_durum"] == "cozuldu":
         raise HTTPException(
        status_code=400,
        detail=(
            "Çözülmüş bir talep "
            "başka personele devredilemez."
        ),
    )
        yeni_personel = dict(
            personel_sonucu._mapping
        )

        mevcut_personel_id = (
            talep.get(
                "talep_atanan_personel_id"
            )
        )

        if (
            mevcut_personel_id is not None
            and str(mevcut_personel_id)
            == str(veri.yeni_personel_id)
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Talep zaten seçilen "
                    "personele atanmış."
                ),
            )

        guncelleme_sorgu = text("""
            UPDATE talepler
            SET
                talep_atanan_personel_id =
                    :yeni_personel_id,
                talep_guncellenme_tarihi =
                    NOW()
            WHERE talep_id = :talep_id;
        """)

        db.execute(
            guncelleme_sorgu,
            {
                "talep_id":
                    veri.talep_id,
                "yeni_personel_id":
                    veri.yeni_personel_id,
            },
        )

        eski_personel_adi = (
            talep.get(
                "eski_personel_adi"
            )
            or "Atanmamış"
        )

        yeni_personel_adi = (
            yeni_personel[
                "kullanici_ad_soyad"
            ]
        )

        log_mesaji = (
            "SİSTEM MESAJI: Talep "
            f"{eski_personel_adi} "
            "personelinden "
            f"{yeni_personel_adi} "
            "personeline devredildi."
        )

        yorum_sorgu = text("""
            INSERT INTO yorumlar (
                yorum_talep_id,
                yorum_kullanici_id,
                yorum_mesaj
            )
            VALUES (
                :talep_id,
                :admin_id,
                :mesaj
            );
        """)

        db.execute(
            yorum_sorgu,
            {
                "talep_id":
                    veri.talep_id,
                "admin_id":
                    admin["kullanici_id"],
                "mesaj":
                    log_mesaji,
            },
        )

        db.commit()

        return {
            "mesaj": (
                "Talep başarıyla "
                "devredildi."
            ),
            "talep_id":
                veri.talep_id,
            "takip_no":
                talep["talep_takip_no"],
            "eski_personel":
                eski_personel_adi,
            "yeni_personel":
                yeni_personel_adi,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Talep devredilirken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()


@app.get(
    "/personel/token-kontrol",
    tags=["Personel"],
)
def personel_token_kontrol(
    personel: dict = Depends(
        personel_token_dogrula
    ),
):
    return {
        "mesaj": "Personel tokenı geçerli.",
        "kullanici_id":
            personel["kullanici_id"],
        "kullanici_eposta":
            personel["kullanici_eposta"],
        "kullanici_ad_soyad":
            personel["kullanici_ad_soyad"],
        "rol":
            personel["rol"],
    }

@app.get(
    "/personel/profil",
    tags=["Personel"],
)
def personel_profili_getir(
    personel: dict = Depends(
        personel_token_dogrula
    ),
):
    db = SessionLocal()

    try:
        profil_sorgu = text("""
            SELECT
                k.kullanici_id,
                k.kullanici_ad_soyad,
                k.kullanici_eposta,
                k.kullanici_rol,
                k.kullanici_departman,
                k.kullanici_olusturulma_tarihi,

                COUNT(t.talep_id)
                    AS toplam_atanan_talep,

                COUNT(t.talep_id) FILTER (
                    WHERE LOWER(
                        TRIM(t.talep_durum)
                    ) = 'cozuldu'
                ) AS toplam_cozulen_talep,

                COUNT(t.talep_id) FILTER (
                    WHERE LOWER(
                        TRIM(t.talep_durum)
                    ) <> 'cozuldu'
                ) AS aktif_talep_sayisi,

                COUNT(t.talep_id) FILTER (
                    WHERE LOWER(
                        TRIM(t.talep_durum)
                    ) = 'cozuldu'
                      AND DATE(
                          t.talep_guncellenme_tarihi
                      ) = CURRENT_DATE
                ) AS bugun_cozulen_talep

            FROM kullanicilar k

            LEFT JOIN talepler t
                ON t.talep_atanan_personel_id =
                   k.kullanici_id

            WHERE k.kullanici_id =
                  :personel_id

            GROUP BY
                k.kullanici_id,
                k.kullanici_ad_soyad,
                k.kullanici_eposta,
                k.kullanici_rol,
                k.kullanici_departman,
                k.kullanici_olusturulma_tarihi;
        """)

        profil_sonucu = db.execute(
            profil_sorgu,
            {
                "personel_id":
                    personel["kullanici_id"],
            },
        ).first()

        if not profil_sonucu:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Personel profili "
                    "bulunamadı."
                ),
            )

        return {
            "mesaj": (
                "Personel profili "
                "başarıyla getirildi."
            ),
            "veri": dict(
                profil_sonucu._mapping
            ),
        }

    finally:
        db.close()

@app.put(
    "/personel/sifre-degistir",
    tags=["Personel"],
)
def personel_sifresini_degistir(
    veri: PersonelSifreDegistirme,
    personel: dict = Depends(
        personel_token_dogrula
    ),
):
    db = SessionLocal()

    try:
        mevcut_sifre = (
            veri.mevcut_sifre.strip()
        )

        yeni_sifre = (
            veri.yeni_sifre.strip()
        )

        if not mevcut_sifre:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Mevcut şifre boş "
                    "bırakılamaz."
                ),
            )

        if len(yeni_sifre) < 8:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Yeni şifre en az "
                    "8 karakter olmalıdır."
                ),
            )

        if mevcut_sifre == yeni_sifre:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Yeni şifre mevcut "
                    "şifreyle aynı olamaz."
                ),
            )

        personel_sorgu = text("""
            SELECT
                kullanici_sifre_hash
            FROM kullanicilar
            WHERE kullanici_id =
                  :personel_id
              AND LOWER(
                  TRIM(kullanici_rol)
              ) = 'personel';
        """)

        personel_sonucu = db.execute(
            personel_sorgu,
            {
                "personel_id":
                    personel["kullanici_id"],
            },
        ).first()

        if not personel_sonucu:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Personel hesabı "
                    "bulunamadı."
                ),
            )

        mevcut_hash = (
            personel_sonucu
            .kullanici_sifre_hash
        )

        sifre_dogru = (
            personel_sifresi_dogrula(
                mevcut_sifre,
                mevcut_hash,
            )
        )

        if not sifre_dogru:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Mevcut şifre hatalı."
                ),
            )

        yeni_hash = (
            personel_sifresi_hashle(
                yeni_sifre
            )
        )

        guncelleme_sorgu = text("""
            UPDATE kullanicilar
            SET kullanici_sifre_hash =
                :yeni_hash
            WHERE kullanici_id =
                  :personel_id;
        """)

        db.execute(
            guncelleme_sorgu,
            {
                "yeni_hash": yeni_hash,
                "personel_id":
                    personel["kullanici_id"],
            },
        )

        db.commit()

        return {
            "mesaj": (
                "Şifreniz başarıyla "
                "güncellendi."
            ),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Şifre değiştirilirken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()

@app.get(
    "/personel/taleplerim",
    tags=["Personel Paneli"],
)
def personelin_taleplerini_getir(
    personel: dict = Depends(
        personel_token_dogrula
    ),
):
    db = SessionLocal()

    try:
        sorgu = text("""
            SELECT
                t.talep_id,
                t.talep_takip_no,
                t.talep_baslik,
                t.talep_ham_icerik,
                t.talep_durum,
                t.talep_kaynak,
                t.talep_gonderen_ad_soyad,
                t.talep_gonderen_eposta,
                t.talep_kategori_id,
                t.talep_olusturulma_tarihi,
                t.talep_guncellenme_tarihi,

                k.kategori_ad,
                k.kategori_departman,

                yz.yz_ozet,
                yz.yz_oncelik_seviyesi,
                yz.yz_duygu_durumu,
                yz.yz_guven_skoru,
                yz.yz_cozum_onerisi,
                yz.yz_musteri_cevabi

            FROM talepler t

            LEFT JOIN kategoriler k
                ON k.kategori_id =
                   t.talep_kategori_id

            LEFT JOIN yz_analizleri yz
                ON yz.yz_talep_id =
                   t.talep_id

            WHERE t.talep_atanan_personel_id =
                  :personel_id

            ORDER BY
                t.talep_olusturulma_tarihi DESC;
        """)

        sonuc = db.execute(
            sorgu,
            {
                "personel_id":
                    personel["kullanici_id"],
            },
        )

        talepler = [
            dict(satir._mapping)
            for satir in sonuc
        ]

        return {
            "mesaj": (
                "Personele atanmış talepler "
                "başarıyla getirildi."
            ),
            "personel": {
                "kullanici_id":
                    personel["kullanici_id"],
                "kullanici_ad_soyad":
                    personel["kullanici_ad_soyad"],
                "kullanici_eposta":
                    personel["kullanici_eposta"],
            },
            "toplam_talep": len(talepler),
            "veri": talepler,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Personel talepleri alınırken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()

# 2. Yönetim Paneli - Dashboard Özeti (GET)
@app.get("/talepler", tags=["Talepler"])
def talepleri_getir(
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()

    try:
        sorgu = text("""
            SELECT
                t.talep_id,
                t.talep_takip_no,
                t.talep_baslik,
                t.talep_ham_icerik,
                t.talep_durum,
                t.talep_kaynak,
                t.talep_gonderen_ad_soyad,
                t.talep_gonderen_eposta,
                t.talep_kullanici_id,
                t.talep_kategori_id,
                t.talep_bildirildi,

                k.kategori_ad,
                k.kategori_departman,

                yz.yz_ozet,
                yz.yz_oncelik_seviyesi,
                yz.yz_oncelik_gerekcesi,
                yz.yz_duygu_durumu,
                yz.yz_guven_skoru,
                yz.yz_cozum_onerisi,
                t.talep_olusturulma_tarihi,
                t.talep_guncellenme_tarihi

            FROM talepler t

            LEFT JOIN kategoriler k
                ON t.talep_kategori_id = k.kategori_id

            LEFT JOIN yz_analizleri yz
                ON t.talep_id = yz.yz_talep_id

            ORDER BY t.talep_olusturulma_tarihi DESC

            LIMIT 100;
        """)

        sonuc = db.execute(sorgu)

        talepler = [
            dict(satir._mapping)
            for satir in sonuc
        ]

        return {
            "mesaj": "Talepler başarıyla getirildi",
            "veri": talepler
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Talepler getirilirken hata oluştu: {str(e)}"
        )

    finally:
        db.close()

@app.get(
    "/personel/talep/{talep_id}",
    tags=["Personel Paneli"],
)
def personel_talep_detayi(
    talep_id: str,
    personel: dict = Depends(
        personel_token_dogrula
    ),
):
    db = SessionLocal()

    try:

        sorgu = text("""
            SELECT

                t.talep_id,
                t.talep_takip_no,
                t.talep_baslik,
                t.talep_ham_icerik,
                t.talep_durum,
                t.talep_kaynak,
                t.talep_gonderen_ad_soyad,
                t.talep_gonderen_eposta,
                t.talep_olusturulma_tarihi,
                t.talep_guncellenme_tarihi,

                k.kategori_ad,
                k.kategori_departman,

                yz.yz_ozet,
                yz.yz_oncelik_seviyesi,
                yz.yz_duygu_durumu,
                yz.yz_guven_skoru,
                yz.yz_cozum_onerisi,
                yz.yz_musteri_cevabi

            FROM talepler t

            LEFT JOIN kategoriler k
                ON k.kategori_id =
                t.talep_kategori_id

            LEFT JOIN yz_analizleri yz
                ON yz.yz_talep_id =
                t.talep_id

            WHERE
                t.talep_id = :talep_id

            AND
                t.talep_atanan_personel_id =
                :personel_id
        """)

        sonuc = db.execute(
            sorgu,
            {
                "talep_id": talep_id,
                "personel_id":
                    personel["kullanici_id"],
            },
        ).first()

        if sonuc is None:

            raise HTTPException(
                status_code=404,
                detail="Talep bulunamadı.",
            )

        return dict(
            sonuc._mapping
        )

    finally:

        db.close()
    
# 3. Filtreli Talepler (GET)
@app.get("/talepler/filtreli", tags=["Talepler"])
def filtreli_talepleri_getir(
    durum: Optional[str] = None,
    oncelik: Optional[str] = None,
    kategori_id: Optional[int] = None,
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        # Tabloları doğrudan JOIN yaparak kolon uyumsuzluklarını ortadan kaldırıyoruz
        sorgu_metni = """
            SELECT 
                t.talep_id,
                t.talep_takip_no,
                t.talep_baslik,
                t.talep_ham_icerik,
                t.talep_durum,
                t.talep_kaynak,
                t.talep_gonderen_ad_soyad,
                t.talep_gonderen_eposta,
                t.talep_kategori_id,
                k.kategori_ad,
                yz.yz_ozet,
                yz.yz_oncelik_seviyesi,
                yz.yz_duygu_durumu,
                yz.yz_guven_skoru,
                t.talep_olusturulma_tarihi,
                t.talep_guncellenme_tarihi
            FROM talepler t
            LEFT JOIN kategoriler k ON t.talep_kategori_id = k.kategori_id
            LEFT JOIN yz_analizleri yz ON t.talep_id = yz.yz_talep_id
            WHERE 1=1
        """
        parametreler = {}
        
        if durum:
            # Fazladan olası boşlukları temizlemek için .strip() ekliyoruz
            sorgu_metni += " AND t.talep_durum = :durum"
            parametreler["durum"] = durum.strip()
            
        if oncelik:
            sorgu_metni += " AND yz.yz_oncelik_seviyesi = :oncelik"
            parametreler["oncelik"] = oncelik.strip()
            
        if kategori_id:
            sorgu_metni += " AND t.talep_kategori_id = :kategori_id"
            parametreler["kategori_id"] = kategori_id
            
        sorgu_metni += " ORDER BY t.talep_olusturulma_tarihi DESC LIMIT 100;"
        
        sonuc = db.execute(text(sorgu_metni), parametreler)
        talepler = [dict(satir._mapping) for satir in sonuc]
        
        return {"mesaj": "Filtrelenmiş talepler getirildi.", "veri": talepler}
    finally:
        db.close()

# 4. Talep Detayı (GET)
@app.get("/talepler/{takip_no}" , tags=["Talepler"])
def talep_detayi_getir(
    takip_no: str,
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        sorgu = text("SELECT * FROM vw_talep_detayi WHERE talep_takip_no = :takip_no;")
        sonuc = db.execute(sorgu, {"takip_no": takip_no}).first()
        if not sonuc:
            raise HTTPException(status_code=404, detail="Böyle bir talep bulunamadı.")
        return {"mesaj": "Talep detayı getirildi", "veri": dict(sonuc._mapping)}
    finally:
        db.close()


# 5. Sisteme Yeni Talep Ekleme (POST) - TAM OTOMATİK
@app.post("/talepler", tags=["Talepler"])
def yeni_talep_ekle(talep: YeniTalep, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        # 1. Tekrar eden talep kontrolü
        if tekrar_eden_talep_kontrol(db, talep.eposta, talep.baslik, talep.icerik): # Eklendi!
            return {
                "mesaj": "Bu talep zaten sistemimizde kayıtlı. Lütfen inceleme sonucunu bekleyin.",
                "durum": "reddedildi"
            }
        
        # 1. SQL Fonksiyonunu (Function) çağır
        sorgu = text("""
            SELECT fn_yeni_talep_olustur(
                :ad_soyad, :eposta, :baslik, :icerik, :kaynak
            )
        """)
        # 2. Veritabanına kaydet ve yeni oluşan UUID'yi (.scalar() ile) hemen al
        yeni_talep_id = db.execute(sorgu, {
            "ad_soyad": talep.ad_soyad,
            "eposta": talep.eposta,
            "baslik": talep.baslik,
            "icerik": talep.icerik,
            "kaynak": talep.kaynak
        }).scalar()
        
        db.commit() 
        
        # 3. YZ Analizini Arka Planda Başlat (API müşteriyi bekletmez)
        background_tasks.add_task(
            talep_analiz_et_ve_uygula, 
            str(yeni_talep_id), 
            talep.baslik, 
            talep.icerik
        )

        return {
            "mesaj": "Yeni destek talebi başarıyla oluşturuldu! Yapay zeka şu an arka planda talebinizi inceliyor.",
            "talep_id": str(yeni_talep_id)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Talep oluşturulurken hata: {str(e)}")
    finally:
        db.close()


# 6. Talebe Yorum/Cevap Ekleme (POST) 
@app.post("/yorumlar" , tags=["Yorumlar"])
def talebe_yorum_ekle(
    yorum: YeniYorum,
    admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id, :kullanici_id, :mesaj, :yeni_durum, :islem_yapan_tipi
            )
        """)
        db.execute(sorgu, {
            "talep_id": yorum.talep_id,
            "kullanici_id": admin["kullanici_id"],
            "mesaj": yorum.mesaj,
            "yeni_durum": yorum.yeni_durum,
            "islem_yapan_tipi": "personel"
        })
        db.commit()
        return {"mesaj": "Yorum işleme alındı ve otomasyon kuralları çalıştırıldı."}
    finally:
        db.close()

# 7. Yönetim Paneli - Dashboard Özeti (GET)
@app.get("/yonetim/paneli/ozeti" , tags=["Yönetim Paneli"])
def yonetim_paneli_ozeti(
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        sorgu = text("SELECT * FROM vw_yonetim_paneli_ozeti;")
        sonuc = db.execute(sorgu)
        ozet = [dict(satir._mapping) for satir in sonuc]
        return {"mesaj": "Yönetim paneli özeti başarıyla getirildi", "veri": ozet}
    finally:
        db.close()

# 8. Kategori İstatistikleri (GET)
@app.get("/kategoriler/istatistikler" , tags=["İstatistikler"])
def kategori_istatistikleri(
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        sorgu = text("SELECT * FROM vw_kategori_istatistikleri;")
        sonuc = db.execute(sorgu)
        istatistikler = [dict(satir._mapping) for satir in sonuc]
        return {"mesaj": "Kategori istatistikleri başarıyla getirildi", "veri": istatistikler}
    finally:
        db.close()

# 9. RAG Arama (GET)
@app.get("/talepler/rag/arama" , tags=["Talepler"])
def talep_rag_arama(
    kelime: str,
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        # 1. Kullanıcıdan gelen metni vektöre dönüştür
        aranan_vektor_listesi = embedding_olustur(kelime)
        
        # 2. Vektörü string formatına çevir
        vektor_str = str(aranan_vektor_listesi)
        
        # 3. ::vector YERİNE CAST KULLANIYORUZ (SQLAlchemy hatasını önlemek için)
        sorgu = text("SELECT * FROM fn_rag_vektor_arama(CAST(:aranan_vektor AS vector), 5);")
        
        sonuc = db.execute(sorgu, {"aranan_vektor": vektor_str})
        talepler = [dict(satir._mapping) for satir in sonuc]
        
        return {"mesaj": "RAG arama sonuçları başarıyla getirildi", "veri": talepler}
    finally:
        db.close()

# 10. Durum Güncelleme (PUT)
@app.put("/talepler/durum-guncelle" , tags=["Talepler"])
def talep_durum_guncelle(
    guncelleme: DurumGuncelleme,
    admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        # 1. Verilen takip_no'ya ait gerçek talep_id'yi (UUID) bulalım
        talep_sorgu = text("SELECT talep_id FROM talepler WHERE talep_takip_no = :takip_no;")
        sonuc = db.execute(talep_sorgu, {"takip_no": guncelleme.takip_no}).first()
        
        if not sonuc:
            raise HTTPException(status_code=404, detail="Böyle bir takip numarasına ait talep bulunamadı.")
        
        gercek_talep_id = sonuc[0]

        # 2. Bulunan gerçek UUID ile durum güncelleme prosedürünü çalıştıralım
        sorgu = text("CALL sp_talep_durum_guncelle(:talep_id, :kullanici_id, :yeni_durum)")
        db.execute(sorgu, {
            "talep_id": gercek_talep_id,
            "kullanici_id": admin["kullanici_id"],
            "yeni_durum": guncelleme.yeni_durum
        })
        db.commit()
        return {"mesaj": f"{guncelleme.takip_no} takip numaralı talebin durumu başarıyla güncellendi"}
    finally:
        db.close()

# 11. Pipeline ve Veritabanı Entegrasyonunu Sağlayan Tam Endpoint
@app.post("/talepler/yapay-zeka-analiz", tags=["Yapay Zeka Analiz"])
def ai_talep_analiz_ve_kaydet(
    talep_id: str,
    baslik: str,
    icerik: str,
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()
    try:
        sonuc = talep_analiz_et_ve_uygula( talep_id, baslik, icerik)

        return {
            "mesaj": sonuc["mesaj"],
            "veri": {
                "talep_id": talep_id,
                "kategori_id": sonuc["kategori_id"],
                "guven_skoru": sonuc["guven_skoru"],
                "cozum_onerisi": sonuc["cozum_onerisi"],
                "onerilen_cevap": sonuc["onerilen_cevap"]
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"YZ analiz hatası: {str(e)}")
    finally:
        db.close()

# 12. Müşteri Çözüm Onayı (Evet/Hayır Butonu İçin)
@app.post("/talepler/musteri-onayi", tags=["Talepler"])
def musteri_cozum_onayini_isle(
    onay: MusteriCozumOnayi,
):
    db = SessionLocal()

    try:
        temiz_talep_id = onay.talep_id.strip()

        if (
            temiz_talep_id.startswith("v")
            or temiz_talep_id.startswith("V")
        ):
            temiz_talep_id = temiz_talep_id[1:]

        yeni_durum = (
            "cozuldu"
            if onay.cozuldu_mu
            else "acik"
        )

        mesaj = (
            "SİSTEM MESAJI: Müşteri sunulan çözümü "
            "onayladı ve talep kapatıldı."
            if onay.cozuldu_mu
            else
            "SİSTEM MESAJI: Müşteri sunulan çözümü "
            "yetersiz buldu. Personel desteği bekleniyor."
        )

        talep_kontrol = db.execute(
            text("""
                SELECT talep_id
                FROM talepler
                WHERE talep_id = :talep_id;
            """),
            {
                "talep_id": temiz_talep_id,
            },
        ).first()

        if not talep_kontrol:
            raise HTTPException(
                status_code=404,
                detail="Geri bildirim yapılacak talep bulunamadı.",
            )

        # Talep durumunu doğrudan güncelle.
        db.execute(
            text("""
                UPDATE talepler
                SET
                    talep_durum = :yeni_durum,
                    talep_guncellenme_tarihi = NOW()
                WHERE talep_id = :talep_id;
            """),
            {
                "talep_id": temiz_talep_id,
                "yeni_durum": yeni_durum,
            },
        )

        # Müşteri geri bildirimini yorumlara kaydet.
        db.execute(
            text("""
                INSERT INTO yorumlar (
                    yorum_talep_id,
                    yorum_mesaj
                )
                VALUES (
                    :talep_id,
                    :mesaj
                );
            """),
            {
                "talep_id": temiz_talep_id,
                "mesaj": mesaj,
            },
        )

        db.commit()

        return {
            "mesaj": (
                "Geri bildiriminiz alındı. "
                f"Talep durumu '{yeni_durum}' "
                "olarak güncellendi."
            ),
            "talep_id": temiz_talep_id,
            "talep_durum": yeni_durum,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "Müşteri geri bildirimi işlenirken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()
# 13. Personel Paneli - Onay Bekleyen Talepler (GET)
@app.get("/personel/onay-bekleyenler", tags=["Personel Paneli"])
def onay_bekleyenleri_getir(
    departman_adi: Optional[str] = None,
    _admin: dict = Depends(admin_token_dogrula),
):
    """
    Durumu 'onay_bekliyor' olan 2. Senaryo taleplerini listeler.
    Opsiyonel olarak departman adına göre filtreleme yapılabilir.
    """
    db = SessionLocal()
    try:
        if departman_adi:
            sorgu = text("SELECT * FROM vw_onay_bekleyen_talepler WHERE kategori_departman = :departman;")
            sonuc = db.execute(sorgu, {"departman": departman_adi})
        else:
            sorgu = text("SELECT * FROM vw_onay_bekleyen_talepler;")
            sonuc = db.execute(sorgu)
            
        talepler = [dict(satir._mapping) for satir in sonuc]
        return {"mesaj": "Onay bekleyen talepler başarıyla getirildi.", "veri": talepler}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veri çekilirken hata oluştu: {str(e)}")
    finally:
        db.close()

# 14. Personel Onay İşlemi ve Müşteriye Gönderim (POST)
@app.post(
    "/personel/onayla-ve-gonder",
    tags=["Personel Paneli"],
)
def personel_cevabi_gonder(
    onay: PersonelOnayIslemi,
    personel: dict = Depends(
    personel_token_dogrula
),
):
    """
    Personelin AI taslağını onaylayıp veya düzenleyip
    müşteriye ilettiği endpoint.

    Yanıtı sisteme kaydeder, müşteriye gerçek e-posta
    gönderir ve talep durumunu
    'musteri_yaniti_bekleniyor' olarak günceller.
    """
    db = SessionLocal()

    try:
        temiz_yanit = onay.yanit_metni.strip()

        if not temiz_yanit:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Gönderilecek yanıt metni "
                    "boş olamaz."
                ),
            )

        talep_sorgu = text("""
    SELECT
        talep_gonderen_ad_soyad,
        talep_gonderen_eposta,
        talep_takip_no,
        talep_baslik
    FROM talepler
    WHERE talep_id = :talep_id
      AND talep_atanan_personel_id = :personel_id;
""")

        talep_sonucu = db.execute(
            talep_sorgu,
            {
    "talep_id": onay.talep_id,
    "personel_id":
        personel["kullanici_id"],
},
        ).first()

        if not talep_sonucu:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Yanıt gönderilecek talep "
                    "bulunamadı."
                ),
            )

        talep_bilgisi = dict(
            talep_sonucu._mapping
        )

        musteri_eposta = talep_bilgisi.get(
            "talep_gonderen_eposta"
        )

        if not musteri_eposta:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Talebe ait müşteri e-posta "
                    "adresi bulunamadı."
                ),
            )

        musteri_adi = (
            talep_bilgisi.get(
                "talep_gonderen_ad_soyad"
            )
            or "Değerli Müşterimiz"
        )

        takip_no = (
            talep_bilgisi.get(
                "talep_takip_no"
            )
            or "Belirtilmemiş"
        )

        talep_basligi = (
            talep_bilgisi.get(
                "talep_baslik"
            )
            or "Destek Talebi"
        )

        eposta_konusu = (
            "Destek Talebiniz Yanıtlandı - "
            f"{takip_no}"
        )

        cozuldu_linki = (
            "http://localhost:5173/"
            "musteri-onayi"
            f"?talep_id={onay.talep_id}"
            "&sonuc=evet"
        )

        cozulmedi_linki = (
            "http://localhost:5173/"
            "musteri-onayi"
            f"?talep_id={onay.talep_id}"
            "&sonuc=hayir"
        )

        eposta_mesaji = f"""Merhaba {musteri_adi},

"{talep_basligi}" başlıklı destek talebiniz yanıtlandı.

Takip Numaranız: {takip_no}

Yanıtımız:
{temiz_yanit}

Lütfen çözüm durumunu belirtin:

Sorunum çözüldü:
{cozuldu_linki}

Sorunum devam ediyor:
{cozulmedi_linki}

Bu e-posta otomatik olarak gönderilmiştir.

Saygılarımızla,
Akıllı Müşteri Destek Ekibi
"""

        print(
            "Gönderilecek adres:",
            musteri_eposta,
        )

        eposta_gonder(
            alici_eposta=musteri_eposta,
            konu=eposta_konusu,
            mesaj=eposta_mesaji,
        )

        yorum_sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id,
                :kullanici_id,
                :mesaj,
                'musteri_yaniti_bekleniyor',
                'personel'
            )
        """)

        log_mesaji = (
            f"[{onay.islem_tipi}]: "
            f"{temiz_yanit}"
        )

        db.execute(
            yorum_sorgu,
            {
                "talep_id": onay.talep_id,
                "kullanici_id":
                    personel["kullanici_id"],
                "mesaj": log_mesaji,
            },
        )

        db.commit()

        return {
            "mesaj": (
                "Yanıt sisteme kaydedildi ve "
                "müşteriye e-posta olarak "
                "gönderildi."
            ),
            "gonderilen_eposta":
                musteri_eposta,
            "takip_no": takip_no,
        }

    except HTTPException:
        db.rollback()
        raise

    except smtplib.SMTPAuthenticationError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "Gmail kimlik doğrulaması "
                "başarısız oldu. SMTP_EMAIL ve "
                "uygulama şifresini kontrol edin."
            ),
        )

    except smtplib.SMTPException as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "E-posta gönderilirken SMTP "
                f"hatası oluştu: {str(e)}"
            ),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "Onay ve gönderim işlemi "
                f"sırasında hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()

# 15. Personel Paneli - İncelenmesi Gereken Talepler (GET)
@app.get("/personel/incelenenler", tags=["Personel Paneli"])
def incelenen_talepleri_getir(
    departman_adi: Optional[str] = None,
    _admin: dict = Depends(admin_token_dogrula),
):
    """
    Durumu 'inceleniyor' olan 3. Senaryo taleplerini listeler.
    Yapay zekanın güven skoru düşük olduğu için (veya Diğer kategorisi) 
    personelin AI taslağını manuel incelemesi gereken kuyruktur.
    """
    db = SessionLocal()
    try:
        if departman_adi:
            sorgu = text("SELECT * FROM vw_incelenen_talepler WHERE kategori_departman = :departman;")
            sonuc = db.execute(sorgu, {"departman": departman_adi})
        else:
            sorgu = text("SELECT * FROM vw_incelenen_talepler;")
            sonuc = db.execute(sorgu)
            
        talepler = [dict(satir._mapping) for satir in sonuc]
        return {"mesaj": "İncelenmesi gereken talepler başarıyla getirildi.", "veri": talepler}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Veri çekilirken hata oluştu: {str(e)}")
    finally:
        db.close()
# 16. Personel İnceleme ve Müşteriye Gönderim (POST)
@app.post(
    "/personel/incelenen-yanitla",
    tags=["Personel Paneli"],
)
def incelenen_talebi_yanitla(
    islem: PersonelOnayIslemi,
    admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()

    try:
        temiz_yanit = islem.yanit_metni.strip()

        if not temiz_yanit:
            raise HTTPException(
                status_code=400,
                detail="Gönderilecek yanıt metni boş olamaz.",
            )

        talep_sorgu = text("""
            SELECT
                talep_gonderen_ad_soyad,
                talep_gonderen_eposta,
                talep_takip_no,
                talep_baslik
            FROM talepler
            WHERE talep_id = :talep_id;
        """)

        talep_sonucu = db.execute(
            talep_sorgu,
            {
                "talep_id": islem.talep_id,
            },
        ).first()

        if not talep_sonucu:
            raise HTTPException(
                status_code=404,
                detail="Yanıt gönderilecek talep bulunamadı.",
            )

        talep_bilgisi = dict(
            talep_sonucu._mapping
        )

        musteri_eposta = talep_bilgisi.get(
            "talep_gonderen_eposta"
        )

        if not musteri_eposta:
            raise HTTPException(
                status_code=400,
                detail="Müşteri e-posta adresi bulunamadı.",
            )

        musteri_adi = (
            talep_bilgisi.get(
                "talep_gonderen_ad_soyad"
            )
            or "Değerli Müşterimiz"
        )

        takip_no = (
            talep_bilgisi.get(
                "talep_takip_no"
            )
            or "Belirtilmemiş"
        )

        talep_basligi = (
            talep_bilgisi.get(
                "talep_baslik"
            )
            or "Destek Talebi"
        )

        eposta_konusu = (
            f"Destek Talebiniz Yanıtlandı - {takip_no}"
        )

        cozuldu_linki = (
            "http://localhost:5173/"
            "musteri-onayi"
            f"?talep_id={islem.talep_id}"
            "&sonuc=evet"
        )

        cozulmedi_linki = (
            "http://localhost:5173/"
            "musteri-onayi"
            f"?talep_id={islem.talep_id}"
            "&sonuc=hayir"
        )

        eposta_mesaji = f"""Merhaba {musteri_adi},

"{talep_basligi}" başlıklı destek talebiniz incelenmiştir.

Takip Numaranız: {takip_no}

Yanıtımız:
{temiz_yanit}

Lütfen çözüm durumunu belirtin:

Sorunum çözüldü:
{cozuldu_linki}

Sorunum devam ediyor:
{cozulmedi_linki}

Bu e-posta otomatik olarak gönderilmiştir.

Saygılarımızla,
Akıllı Müşteri Destek Ekibi
"""

        eposta_gonder(
            alici_eposta=musteri_eposta,
            konu=eposta_konusu,
            mesaj=eposta_mesaji,
        )

        yorum_sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id,
                :kullanici_id,
                :mesaj,
                'musteri_yaniti_bekleniyor',
                'personel'
            )
        """)

        log_mesaji = (
            f"[MANUEL_INCELEME_YANITI]: "
            f"{temiz_yanit}"
        )

        db.execute(
            yorum_sorgu,
            {
                "talep_id": islem.talep_id,
                "kullanici_id":
                    admin["kullanici_id"],
                "mesaj": log_mesaji,
            },
        )

        db.commit()

        return {
            "mesaj": (
                "Manuel yanıt müşteriye e-posta olarak "
                "gönderildi ve talep müşteri yanıtı "
                "bekleniyor durumuna geçirildi."
            ),
            "gonderilen_eposta":
                musteri_eposta,
            "takip_no": takip_no,
        }

    except HTTPException:
        db.rollback()
        raise

    except smtplib.SMTPAuthenticationError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "Gmail kimlik doğrulaması başarısız oldu. "
                "SMTP ayarlarını kontrol edin."
            ),
        )

    except smtplib.SMTPException as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "E-posta gönderilirken SMTP hatası "
                f"oluştu: {str(e)}"
            ),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "İnceleme yanıtı gönderilirken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()
# 17. Personel Paneli - Talep Yönlendirme (PUT)
@app.put("/personel/talep-yonlendir", tags=["Personel Paneli"])
def departmana_yonlendir(
    islem: TalepYonlendirme,
    admin: dict = Depends(admin_token_dogrula),
):
    """
    Personelin yanlış departmana gelmiş bir talebi, 
    doğru kategoriye (dolayısıyla departmana) yönlendirmesini sağlar.
    """
    db = SessionLocal()
    try:
        # 1. Talebin kategorisini güncelle
        guncelle_sorgu = text("""
            UPDATE talepler 
            SET talep_kategori_id = :yeni_kategori_id 
            WHERE talep_id = :talep_id
        """)
        db.execute(guncelle_sorgu, {
            "yeni_kategori_id": islem.yeni_kategori_id,
            "talep_id": islem.talep_id
        })

        # 2. Bu yönlendirme işlemini yorumlar/log tablosuna sistem mesajı olarak ekle
        log_sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id, :kullanici_id, :mesaj, NULL, 'personel'
            )
        """)
        db.execute(log_sorgu, {
            "talep_id": islem.talep_id,
            "kullanici_id": admin["kullanici_id"],
            "mesaj": f"[YÖNLENDİRME]: {islem.mesaj}"
        })
        
        db.commit()
        return {"mesaj": "Talep başarıyla yeni departmana yönlendirildi."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Yönlendirme sırasında hata: {str(e)}")
    finally:
        db.close()

# 18. Kategoriler Listesi (GET)
@app.get("/kategoriler", tags=["Kategoriler"])
def tum_kategorileri_getir(
    _admin: dict = Depends(admin_token_dogrula),
):
    """
    Sistemdeki tüm kategorileri (departman bilgileriyle birlikte) listeler.
    Arayüzdeki yönlendirme (dropdown) menülerini doldurmak için kullanılır.
    """
    db = SessionLocal()
    try:
        sorgu = text("SELECT kategori_id, kategori_ad, kategori_departman FROM kategoriler ORDER BY kategori_id ASC;")
        sonuc = db.execute(sorgu)
        kategoriler = [dict(satir._mapping) for satir in sonuc]
        return {"mesaj": "Kategori listesi başarıyla getirildi.", "veri": kategoriler}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kategoriler çekilirken hata: {str(e)}")
    finally:
        db.close()
# 19. Dashboard İstatistikleri (GET)
@app.get(
    "/dashboard/istatistikler",
    tags=["Dashboard"],
)
def dashboard_istatistikleri(
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()

    try:
        # 1. Talep durumlarına göre bütün sayaçlar
        durum_sayilari_sorgu = text("""
            SELECT
                COUNT(*) AS toplam_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(talep_durum))
                        IN ('acik', 'açık')
                ) AS acik_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(talep_durum)) =
                        'onay_bekliyor'
                ) AS onay_bekleyen_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(talep_durum)) =
                        'inceleniyor'
                ) AS incelenen_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(talep_durum)) =
                        'otomatik_yanitlandi'
                ) AS otomatik_yanitlanan_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(talep_durum)) =
                        'musteri_yaniti_bekleniyor'
                ) AS musteri_yaniti_bekleyen_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(talep_durum)) =
                        'cozuldu'
                ) AS cozulen_talep_sayisi,

                COUNT(*) FILTER (
                    WHERE talep_olusturulma_tarihi
                        >= NOW() - INTERVAL '24 hours'
                ) AS son_24_saat_talep_sayisi

            FROM talepler;
        """)

        durum_sayilari_sonucu = db.execute(
            durum_sayilari_sorgu
        ).first()

        # 2. Yapay zekâ tarafından analiz edilen talep sayısı
        ai_analiz_sorgu = text("""
            SELECT COUNT(DISTINCT yz_talep_id)
            FROM yz_analizleri;
        """)

        ai_analiz_edilen_talep_sayisi = (
            db.execute(ai_analiz_sorgu).scalar() or 0
        )

        # 3. Kritik öncelikli talep sayısı
        kritik_sorgu = text("""
            SELECT COUNT(DISTINCT yz_talep_id)
            FROM yz_analizleri
            WHERE LOWER(
                TRIM(yz_oncelik_seviyesi)
            ) = 'kritik';
        """)

        kritik_talep_sayisi = (
            db.execute(kritik_sorgu).scalar() or 0
        )

        # 4. Kategorilere göre talep dağılımı
        kategori_sorgu = text("""
            SELECT
                COALESCE(
                    k.kategori_ad,
                    'Kategorisiz'
                ) AS kategori,

                COUNT(*) AS talep_sayisi

            FROM talepler t

            LEFT JOIN kategoriler k
                ON t.talep_kategori_id =
                   k.kategori_id

            GROUP BY
                k.kategori_ad

            ORDER BY
                talep_sayisi DESC;
        """)

        kategori_sonucu = db.execute(
            kategori_sorgu
        )

        kategori_dagilimi = [
            {
                "kategori": satir.kategori,
                "talep_sayisi":
                    satir.talep_sayisi,
            }
            for satir in kategori_sonucu
        ]

        # 5. Personellere göre talep dağılımı
        personel_sorgu = text("""
            SELECT
                k.kullanici_id
                    AS personel_id,

                k.kullanici_ad_soyad
                    AS personel_adi,

                COUNT(t.talep_id)
                    AS talep_sayisi

            FROM kullanicilar k

            LEFT JOIN talepler t
                ON t.talep_atanan_personel_id =
                   k.kullanici_id

            WHERE LOWER(
                TRIM(k.kullanici_rol)
            ) = 'personel'

            GROUP BY
                k.kullanici_id,
                k.kullanici_ad_soyad

            ORDER BY
                talep_sayisi DESC,
                k.kullanici_ad_soyad ASC;
        """)

        personel_sonucu = db.execute(
            personel_sorgu
        )

        personel_dagilimi = [
            {
                "personel_id":
                    str(satir.personel_id),

                "personel_adi":
                    satir.personel_adi,

                "talep_sayisi":
                    satir.talep_sayisi,
            }
            for satir in personel_sonucu
        ]

        # 6. Ortalama ilk yanıt bekleme süresi
        ortalama_sure_sorgu = text("""
            SELECT
                AVG(
                    ilk_yorum.ilk_yorum_tarihi
                    - t.talep_olusturulma_tarihi
                ) AS ortalama_yanit_bekleme_suresi

            FROM talepler t

            JOIN (
                SELECT
                    yorum_talep_id,

                    MIN(
                        yorum_olusturulma_tarihi
                    ) AS ilk_yorum_tarihi

                FROM yorumlar

                GROUP BY
                    yorum_talep_id
            ) ilk_yorum
                ON ilk_yorum.yorum_talep_id =
                   t.talep_id;
        """)

        ortalama_sure = db.execute(
            ortalama_sure_sorgu
        ).scalar()

        if ortalama_sure:
            toplam_saniye = int(
                ortalama_sure.total_seconds()
            )

            gun = toplam_saniye // 86400
            kalan_saniye = toplam_saniye % 86400

            saat = kalan_saniye // 3600
            kalan_saniye = kalan_saniye % 3600

            dakika = kalan_saniye // 60

            ortalama_yanit_bekleme_suresi = (
                f"{gun} Gün {saat} Saat "
                f"{dakika} Dakika"
            )
        else:
            ortalama_yanit_bekleme_suresi = (
                "Henüz yanıt verisi yok"
            )

        return {
            "mesaj": (
                "Dashboard istatistikleri "
                "başarıyla getirildi."
            ),
            "veri": {
                "toplam_talep_sayisi":
                    durum_sayilari_sonucu
                    .toplam_talep_sayisi,

                "acik_talep_sayisi":
                    durum_sayilari_sonucu
                    .acik_talep_sayisi,

                "onay_bekleyen_talep_sayisi":
                    durum_sayilari_sonucu
                    .onay_bekleyen_talep_sayisi,

                "incelenen_talep_sayisi":
                    durum_sayilari_sonucu
                    .incelenen_talep_sayisi,

                "otomatik_yanitlanan_talep_sayisi":
                    durum_sayilari_sonucu
                    .otomatik_yanitlanan_talep_sayisi,

                "musteri_yaniti_bekleyen_talep_sayisi":
                    durum_sayilari_sonucu
                    .musteri_yaniti_bekleyen_talep_sayisi,

                "cozulen_talep_sayisi":
                    durum_sayilari_sonucu
                    .cozulen_talep_sayisi,

                "son_24_saat_talep_sayisi":
                    durum_sayilari_sonucu
                    .son_24_saat_talep_sayisi,

                "kritik_talep_sayisi":
                    kritik_talep_sayisi,

                "ai_analiz_edilen_talep_sayisi":
                    ai_analiz_edilen_talep_sayisi,

                "ortalama_yanit_bekleme_suresi":
                    ortalama_yanit_bekleme_suresi,

                "kategori_dagilimi":
                    kategori_dagilimi,

                "personel_dagilimi":
                    personel_dagilimi,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Dashboard istatistikleri alınırken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()
 #20. Dashboard - Geciken Talepler (GET)
@app.get(
    "/dashboard/geciken-talepler",
    tags=["Dashboard"],
)
def geciken_talepleri_getir(
    _admin: dict = Depends(admin_token_dogrula),
):
    db = SessionLocal()

    try:
        sorgu = text("""
            SELECT
                talep_id,
                talep_takip_no,
                talep_baslik,
                talep_durum,
                yz_oncelik_seviyesi,
                bekleme_suresi,
                gecikme_seviyesi,
                gecikme_nedeni
            FROM vw_geciken_talepler
            WHERE gecikme_seviyesi <> 'normal'
            ORDER BY bekleme_suresi DESC
            LIMIT 5;
        """)

        sonuc = db.execute(sorgu)

        geciken_talepler = []

        for satir in sonuc:
            kayit = dict(satir._mapping)

            bekleme_suresi = kayit.get(
                "bekleme_suresi"
            )

            if bekleme_suresi:
                toplam_saniye = int(
                    bekleme_suresi.total_seconds()
                )

                gun = toplam_saniye // 86400
                kalan_saniye = toplam_saniye % 86400

                saat = kalan_saniye // 3600
                kalan_saniye = kalan_saniye % 3600

                dakika = kalan_saniye // 60

                if gun > 0:
                    bekleme_metni = (
                        f"{gun} gün {saat} saat "
                        f"{dakika} dakika"
                    )
                elif saat > 0:
                    bekleme_metni = (
                        f"{saat} saat {dakika} dakika"
                    )
                else:
                    bekleme_metni = (
                        f"{dakika} dakika"
                    )
            else:
                bekleme_metni = "Belirtilmemiş"

            kayit["bekleme_suresi"] = (
                bekleme_metni
            )

            geciken_talepler.append(kayit)

        return {
            "mesaj": (
                "Geciken talepler başarıyla getirildi."
            ),
            "veri": geciken_talepler,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=(
                "Geciken talepler alınırken "
                f"hata oluştu: {str(e)}"
            ),
        )

    finally:
        db.close()