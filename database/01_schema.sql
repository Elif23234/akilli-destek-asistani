-- 1. Kullanıcılar Tablosu
CREATE TABLE IF NOT EXISTS kullanicilar (
    kullanici_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kullanici_eposta VARCHAR(255) UNIQUE NOT NULL,
    kullanici_sifre_hash VARCHAR(255) NOT NULL,
    kullanici_ad_soyad VARCHAR(255) NOT NULL,
    kullanici_rol VARCHAR(50) NOT NULL DEFAULT 'kullanici', 
    kullanici_olusturulma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Kategoriler Tablosu
CREATE TABLE IF NOT EXISTS kategoriler (
    kategori_id SERIAL PRIMARY KEY,
    kategori_ad VARCHAR(100) UNIQUE NOT NULL,
    kategori_aciklama TEXT,
    kategori_riskli BOOLEAN DEFAULT FALSE, 
    kategori_departman VARCHAR(100) DEFAULT 'Genel Destek',
    kategori_olusturulma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Talepler Tablosu (Ana Tablo)
CREATE TABLE IF NOT EXISTS talepler (
    talep_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    talep_takip_no VARCHAR(50) UNIQUE NOT NULL, 
    talep_baslik VARCHAR(255) NOT NULL,
    talep_ham_icerik TEXT NOT NULL,
    talep_durum VARCHAR(50) NOT NULL DEFAULT 'acik', 
    talep_kaynak VARCHAR(50) NOT NULL, 
    talep_gonderen_ad_soyad VARCHAR(255) NOT NULL,
    talep_gonderen_eposta VARCHAR(255) NOT NULL,
    talep_kullanici_id UUID REFERENCES kullanicilar(kullanici_id) ON DELETE SET NULL,
    talep_kategori_id INT REFERENCES kategoriler(kategori_id) ON DELETE SET NULL,
    talep_bildirildi BOOLEAN DEFAULT FALSE,
    talep_olusturulma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    talep_guncellenme_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_talepler_durum ON talepler(talep_durum);
CREATE INDEX IF NOT EXISTS idx_talepler_tarih ON talepler(talep_olusturulma_tarihi);

-- 4. Yapay Zeka Analizleri Tablosu
CREATE TABLE IF NOT EXISTS yz_analizleri (
    yz_analiz_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    yz_talep_id UUID UNIQUE NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    yz_ozet TEXT,
    yz_oncelik_skoru FLOAT DEFAULT 0.0,
    yz_oncelik_seviyesi VARCHAR(50) DEFAULT 'Düşük', 
    yz_duygu_durumu VARCHAR(50), 
    yz_guven_skoru FLOAT DEFAULT 0.0,
    yz_cozum_onerisi TEXT, 
    yz_musteri_cevabi TEXT,
    yz_analiz_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Talep Vektörleri Tablosu (RAG İçin)
CREATE TABLE IF NOT EXISTS talep_vektorleri (
    vektor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vektor_talep_id UUID NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    vektor_deger vector(768), 
    vektor_metin_parcasi TEXT NOT NULL,
    vektor_olusturulma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Benzer Talepler Tablosu
CREATE TABLE IF NOT EXISTS benzer_talepler (
    benzerlik_id SERIAL PRIMARY KEY,
    ana_talep_id UUID NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    benzer_talep_id UUID NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    benzerlik_skoru FLOAT NOT NULL,
    benzerlik_eslesme_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT essiz_benzerlik_eslesme UNIQUE (ana_talep_id, benzer_talep_id)
);

-- 7. Yorumlar ve Temsilci Mesajları Tablosu
CREATE TABLE IF NOT EXISTS yorumlar (
    yorum_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    yorum_talep_id UUID NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    yorum_kullanici_id UUID REFERENCES kullanicilar(kullanici_id) ON DELETE CASCADE, --  NOT NULL kısıtlaması kaldırıldı
    yorum_mesaj TEXT NOT NULL,
    yorum_olusturulma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. İşlem Kayıtları Tablosu (Loglama)
CREATE TABLE IF NOT EXISTS islem_kayitlari (
    islem_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    islem_talep_id UUID NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    islem_kullanici_id UUID REFERENCES kullanicilar(kullanici_id) ON DELETE SET NULL,
    islem_tipi VARCHAR(50) DEFAULT 'SİSTEM_İSLEMi',
    islem_eski_durum VARCHAR(50),
    islem_yeni_durum VARCHAR(50),
    islem_aciklama TEXT,
    islem_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Bildirim Kayıtları Tablosu
CREATE TABLE IF NOT EXISTS bildirim_kayitlari (
    bildirim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bildirim_talep_id UUID NOT NULL REFERENCES talepler(talep_id) ON DELETE CASCADE,
    bildirim_kanal VARCHAR(50) NOT NULL, 
    bildirim_hash VARCHAR(64) UNIQUE NOT NULL,
    bildirim_gonderilme_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bildirim_durum VARCHAR(50) NOT NULL 
);