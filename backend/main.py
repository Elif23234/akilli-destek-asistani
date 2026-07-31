from fastapi import FastAPI, HTTPException, BackgroundTasks,Depends
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from sqlalchemy import text
from ai_service import talep_analiz_et_ve_uygula, tekrar_eden_talep_kontrol
from ai_motoru.embedding import embedding_olustur
from fastapi.middleware.cors import CORSMiddleware
from security import (
    admin_bilgilerini_dogrula,
    admin_token_olustur,
    admin_token_dogrula,
)

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
class YeniYorum(BaseModel):
    talep_id: str
    kullanici_id: Optional[str] = None 
    mesaj: str
    yeni_durum: Optional[str] = None
    islem_yapan_tipi: str = "personel" # musteri, personel, yz
class DurumGuncelleme(BaseModel):
    takip_no: str
    kullanici_id: str
    yeni_durum: str
class MusteriCozumOnayi(BaseModel):
    talep_id: str
    cozuldu_mu: bool

class PersonelOnayIslemi(BaseModel):
    talep_id: str
    personel_id: str
    yanit_metni: str
    islem_tipi: str = "AI_YANITI_ONAYLANDI"

class TalepYonlendirme(BaseModel):
    talep_id: str
    personel_id: str
    yeni_kategori_id: int
    mesaj: str = "Talep yanlış departmana geldiği için ilgili birime yönlendirildi."

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


@app.get("/admin/token-kontrol", tags=["Admin"])
def admin_token_kontrol(
    kullanici_adi: str = Depends(admin_token_dogrula),
):
    return {
        "mesaj": "Yönetici tokenı geçerli.",
        "kullanici_adi": kullanici_adi,
    }

# 2. Yönetim Paneli - Dashboard Özeti (GET)
@app.get("/talepler", tags=["Talepler"])
def talepleri_getir():
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

# 3. Filtreli Talepler (GET)
@app.get("/talepler/filtreli", tags=["Talepler"])
def filtreli_talepleri_getir(
    durum: Optional[str] = None,
    oncelik: Optional[str] = None,
    kategori_id: Optional[int] = None
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
def talep_detayi_getir(takip_no: str):
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
def talebe_yorum_ekle(yorum: YeniYorum):
    db = SessionLocal()
    try:
        sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id, :kullanici_id, :mesaj, :yeni_durum, :islem_yapan_tipi
            )
        """)
        db.execute(sorgu, {
            "talep_id": yorum.talep_id,
            "kullanici_id": yorum.kullanici_id,
            "mesaj": yorum.mesaj,
            "yeni_durum": yorum.yeni_durum,
            "islem_yapan_tipi": yorum.islem_yapan_tipi
        })
        db.commit()
        return {"mesaj": "Yorum işleme alındı ve otomasyon kuralları çalıştırıldı."}
    finally:
        db.close()

# 7. Yönetim Paneli - Dashboard Özeti (GET)
@app.get("/yonetim/paneli/ozeti" , tags=["Yönetim Paneli"])
def yonetim_paneli_ozeti():
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
def kategori_istatistikleri():
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
def talep_rag_arama(kelime: str):
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
def talep_durum_guncelle(guncelleme: DurumGuncelleme):
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
            "kullanici_id": guncelleme.kullanici_id,
            "yeni_durum": guncelleme.yeni_durum
        })
        db.commit()
        return {"mesaj": f"{guncelleme.takip_no} takip numaralı talebin durumu başarıyla güncellendi"}
    finally:
        db.close()

# 11. Pipeline ve Veritabanı Entegrasyonunu Sağlayan Tam Endpoint
@app.post("/talepler/yapay-zeka-analiz", tags=["Yapay Zeka Analiz"])
def ai_talep_analiz_ve_kaydet(talep_id: str, baslik: str, icerik: str):
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
def musteri_cozum_onayini_isle(onay: MusteriCozumOnayi):
    db = SessionLocal()
    try:
        # Gelen talep_id'nin başında fazladan 'v' harfi kalmışsa temizleyelim
        temiz_talep_id = onay.talep_id.strip()
        if temiz_talep_id.startswith("v") or temiz_talep_id.startswith("V"):
            temiz_talep_id = temiz_talep_id[1:]

        # Müşteri 'Evet' derse çözüldü, 'Hayır' derse tekrar açılır
        yeni_durum = "cozuldu" if onay.cozuldu_mu else "acik"
        mesaj = "SİSTEM MESAJI: Müşteri sunulan çözümü onayladı ve talep kapatıldı." if onay.cozuldu_mu else "SİSTEM MESAJI: Müşteri sunulan çözümü yetersiz buldu. Personel desteği bekleniyor."
        
        # SQL prosedürünü 'musteri' yetkisiyle çağırıyoruz
        sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id, NULL, :mesaj, :yeni_durum, 'musteri'
            )
        """)
        db.execute(sorgu, {
            "talep_id": temiz_talep_id,
            "mesaj": mesaj,
            "yeni_durum": yeni_durum
        })
        db.commit()
        return {"mesaj": f"Geri bildiriminiz alındı. Talep durumu '{yeni_durum}' olarak güncellendi."}
    finally:
        db.close()

# 13. Personel Paneli - Onay Bekleyen Talepler (GET)
@app.get("/personel/onay-bekleyenler", tags=["Personel Paneli"])
def onay_bekleyenleri_getir(departman_adi: Optional[str] = None):
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
@app.post("/personel/onayla-ve-gonder", tags=["Personel Paneli"])
def personel_cevabi_gonder(onay: PersonelOnayIslemi):
    """
    Personelin AI taslağını onaylayıp veya düzenleyip müşteriye ilettiği endpoint.
    Kullanıcıya bildirim gitmesi için durumu 'musteri_yaniti_bekleniyor' yapar.
    """
    db = SessionLocal()
    try:
        # Yanıtı 'yorumlar' tablosuna müşteri görecek şekilde ekle
        # ve statüyü 1. senaryodaki gibi geri bildirim alınabilecek konuma çek!
        sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id, :kullanici_id, :mesaj, 'musteri_yaniti_bekleniyor', 'personel'
            )
        """)
        
        log_mesaji = f"[{onay.islem_tipi}]: {onay.yanit_metni}"
        
        db.execute(sorgu, {
            "talep_id": onay.talep_id,
            "kullanici_id": onay.personel_id,
            "mesaj": log_mesaji
        })
        
        db.commit()
        return {
            "mesaj": "Yanıt müşteriye başarıyla iletildi. 'Sorun Çözüldü mü?' geri bildirimi bekleniyor."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Onay işlemi sırasında hata: {str(e)}")
    finally:
        db.close()

# 15. Personel Paneli - İncelenmesi Gereken Talepler (GET)
@app.get("/personel/incelenenler", tags=["Personel Paneli"])
def incelenen_talepleri_getir(departman_adi: Optional[str] = None):
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
@app.post("/personel/incelenen-yanitla", tags=["Personel Paneli"])
def incelenen_talebi_yanitla(islem: PersonelOnayIslemi):
    """
    Personelin, YZ'nin kararsız kaldığı talebi inceleyip
    hazırladığı nihai yanıtı müşteriye gönderdiği endpoint.
    Durumu 'musteri_yaniti_bekleniyor' statüsüne geçirir.
    """
    db = SessionLocal()
    try:
        # Yanıtı 'yorumlar' tablosuna müşteri görecek şekilde ekle
        # ve statüyü 1. ve 2. senaryodaki gibi standart döngüye sok
        sorgu = text("""
            CALL sp_talebe_yorum_ekle(
                :talep_id, :kullanici_id, :mesaj, 'musteri_yaniti_bekleniyor', 'personel'
            )
        """)
        
        # Log mesajını manuel müdahale olduğunu belirtecek şekilde etiketliyoruz
        log_mesaji = f"[MANUEL_INCELEME_YANITI]: {islem.yanit_metni}"
        
        db.execute(sorgu, {
            "talep_id": islem.talep_id,
            "kullanici_id": islem.personel_id,
            "mesaj": log_mesaji
        })
        
        db.commit()
        return {
            "mesaj": "Manuel inceleme tamamlandı ve yanıt müşteriye iletildi. 'Sorun Çözüldü mü?' geri bildirimi bekleniyor."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"İnceleme yanıtı gönderilirken hata: {str(e)}")
    finally:
        db.close()

# 17. Personel Paneli - Talep Yönlendirme (PUT)
@app.put("/personel/talep-yonlendir", tags=["Personel Paneli"])
def departmana_yonlendir(islem: TalepYonlendirme):
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
            "kullanici_id": islem.personel_id,
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
def tum_kategorileri_getir():
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
@app.get("/dashboard/istatistikler", tags=["Dashboard"])
def dashboard_istatistikleri():
    db = SessionLocal()

    try:
        # 1. Son 24 saatte gelen talep sayısı
        son_24_saat_sorgu = text("""
            SELECT COUNT(*) AS talep_sayisi
            FROM talepler
            WHERE talep_olusturulma_tarihi >= NOW() - INTERVAL '24 hours';
        """)

        son_24_saat_sonuc = db.execute(son_24_saat_sorgu).scalar()
        son_24_saat_talep_sayisi = son_24_saat_sonuc or 0

        # 2. Kritik talep sayısı
        kritik_sorgu = text("""
            SELECT COUNT(*) AS kritik_talep_sayisi
            FROM yz_analizleri
            WHERE LOWER(yz_oncelik_seviyesi) = 'kritik';
        """)

        kritik_sonuc = db.execute(kritik_sorgu).scalar()
        kritik_talep_sayisi = kritik_sonuc or 0

        # 3. Kategorilere göre talep dağılımı
        kategori_sorgu = text("""
            SELECT
                COALESCE(k.kategori_ad, 'Kategorisiz') AS kategori,
                COUNT(*) AS talep_sayisi
            FROM talepler t
            LEFT JOIN kategoriler k
                ON t.talep_kategori_id = k.kategori_id
            GROUP BY k.kategori_ad
            ORDER BY talep_sayisi DESC;
        """)

        kategori_sonuc = db.execute(kategori_sorgu)

        kategori_dagilimi = [
            {
                "kategori": satir.kategori,
                "talep_sayisi": satir.talep_sayisi
            }
            for satir in kategori_sonuc
        ]

        # 4. Ortalama ilk yanıt bekleme süresi
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
                    MIN(yorum_olusturulma_tarihi) AS ilk_yorum_tarihi
                FROM yorumlar
                GROUP BY yorum_talep_id
            ) ilk_yorum
                ON ilk_yorum.yorum_talep_id = t.talep_id;
        """)

        ortalama_sure = db.execute(ortalama_sure_sorgu).scalar()

        # PostgreSQL interval değeri Python'da timedelta olarak gelir.
        if ortalama_sure:
            toplam_saniye = int(ortalama_sure.total_seconds())

            gun = toplam_saniye // 86400
            kalan_saniye = toplam_saniye % 86400

            saat = kalan_saniye // 3600
            kalan_saniye = kalan_saniye % 3600

            dakika = kalan_saniye // 60

            ortalama_yanit_bekleme_suresi = (
                f"{gun} Gün {saat} Saat {dakika} Dakika"
            )
        else:
            ortalama_yanit_bekleme_suresi = "Henüz yanıt verisi yok"

        return {
            "mesaj": "Dashboard istatistikleri başarıyla getirildi.",
            "veri": {
                "son_24_saat_talep_sayisi": son_24_saat_talep_sayisi,
                "kritik_talep_sayisi": kritik_talep_sayisi,
                "ortalama_yanit_bekleme_suresi": ortalama_yanit_bekleme_suresi,
                "kategori_dagilimi": kategori_dagilimi
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard istatistikleri alınırken hata oluştu: {str(e)}"
        )

    finally:
        db.close()

