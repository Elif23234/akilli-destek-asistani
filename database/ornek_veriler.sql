-- ==========================================
-- SİSTEM BAŞLANGIÇ VERİLERİ (SEED DATA)
-- ==========================================

-- Kategoriler Seed Data
INSERT INTO kategoriler (kategori_ad, kategori_aciklama, kategori_riskli, kategori_departman) VALUES 
('Hesap ve Güvenlik', 'Şifre sıfırlama, profil güncelleme, 2FA ve hesaba erişim sorunları', TRUE, 'Hesap ve Güvenlik'),
('Teknik Sorunlar', 'Sistem hataları, sayfa yüklenmemesi, API bağlantı ve entegrasyon sorunları', FALSE, 'Teknik Destek'),
('Ödeme ve Faturalandırma', 'Başarısız ödemeler, mükerrer çekimler, bakiye ve fatura talepleri', TRUE, 'Finans'),
('İade ve İptal', 'Hizmet/ürün iptali, abonelik sonlandırma ve para iadesi talepleri', TRUE, 'İade Operasyonları'),
('Sipariş ve Teslimat', 'Sipariş durumu, kargo takibi, eksik veya yanlış ürün gönderimi', FALSE, 'Lojistik'),
('Bilgi ve Rehberlik', 'Ürün özellikleri, kullanım kılavuzu, fiyatlandırma ve genel sorular', FALSE, 'Genel Destek'),
('Şikayet ve Geri Bildirim', 'Müşteri memnuniyetsizliği, personel şikayetleri ve sistem önerileri', TRUE, 'Müşteri Deneyimi'),
('Diğer', 'Mevcut kategorilere uymayan istisnai durumlar', TRUE, 'Genel Destek') -- Riskli yapıldı
ON CONFLICT (kategori_ad) DO UPDATE 
SET kategori_riskli = EXCLUDED.kategori_riskli,
    kategori_departman = EXCLUDED.kategori_departman;


-- ==========================================
-- PERSONEL BAŞLANGIÇ VERİLERİ (SEED DATA)
-- Sabit UUID'ler sayesinde Swagger testleriniz asla bozulmaz.
-- ==========================================

INSERT INTO kullanicilar (kullanici_id, kullanici_eposta, kullanici_sifre_hash, kullanici_ad_soyad, kullanici_rol) VALUES 
-- Adminler (Sistem Yönetimi ve Genel Kontrol)
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'admin@destek.com', 'hash_sifre_admin1', 'Ahmet Yılmaz (Sistem Yöneticisi)', 'admin'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'yonetici@destek.com', 'hash_sifre_admin2', 'Selin Demir (Operasyon Müdürü)', 'admin'),

-- Hesap ve Güvenlik Kategorisi İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03', 'guvenlik@destek.com', 'hash_sifre_guvenlik', 'Mert Güven (Güvenlik Uzmanı)', 'personel'),

-- Teknik Sorunlar Kategorisi İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'teknik@destek.com', 'hash_sifre_teknik', 'Caner Arslan (Kıdemli Sistem Uzmanı)', 'personel'),

-- Ödeme ve Faturalandırma Kategorisi İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05', 'finans@destek.com', 'hash_sifre_finans', 'Deniz Kaya (Finans ve Fatura Sorumlusu)', 'personel'),

-- İade ve İptal Kategorisi İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a06', 'iade@destek.com', 'hash_sifre_iade', 'Burcu Çelik (İade Operasyonları)', 'personel'),

-- Sipariş ve Teslimat Kategorisi İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a07', 'lojistik@destek.com', 'hash_sifre_lojistik', 'Emre Kargo (Lojistik ve Sevkiyat Sorumlusu)', 'personel'),

-- Bilgi, Rehberlik ve Diğer Kategoriler İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a08', 'destek@destek.com', 'hash_sifre_destek', 'Zeynep Aksoy (Genel Destek Uzmanı)', 'personel'),

-- Şikayet ve İletişim/Halkla İlişkiler İçin
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a09', 'iletisim@destek.com', 'hash_sifre_iletisim', 'Cemre İletişim (Müşteri Deneyimi Sorumlusu)', 'personel')

ON CONFLICT (kullanici_eposta) DO NOTHING;