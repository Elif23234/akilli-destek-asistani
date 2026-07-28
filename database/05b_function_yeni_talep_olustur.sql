CREATE OR REPLACE FUNCTION fn_yeni_talep_olustur(
    p_ad_soyad VARCHAR,
    p_eposta VARCHAR,
    p_baslik VARCHAR,
    p_icerik TEXT,
    p_kaynak VARCHAR
) RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_takip_no VARCHAR(50);
    v_kategori_id INT := 8; -- Varsayılan 'Diğer'
    v_yeni_talep_id UUID;
BEGIN
    -- 1. Benzersiz Takip Numarası Oluştur
    v_takip_no := 'TKT-' || UPPER(SUBSTRING(MD5(RANDOM()::TEXT) FROM 1 FOR 8));

    -- 2. Talebi Veritabanına Ekle ve ID'yi Yakala (RETURNING ile)
    INSERT INTO talepler (
        talep_takip_no, talep_baslik, talep_ham_icerik, talep_durum,
        talep_kaynak, talep_gonderen_ad_soyad, talep_gonderen_eposta, talep_kategori_id
    ) VALUES (
        v_takip_no, p_baslik, p_icerik, 'acik',
        p_kaynak, p_ad_soyad, p_eposta, v_kategori_id
    ) RETURNING talep_id INTO v_yeni_talep_id;

    -- 3. İşlem Kaydı (Log) Düş
    INSERT INTO islem_kayitlari (
        islem_talep_id, islem_tipi, islem_eski_durum, islem_yeni_durum, islem_aciklama
    ) VALUES (
        v_yeni_talep_id, 'SİSTEM_İSLEMi', NULL, 'acik', 'Müşteri tarafından yeni talep oluşturuldu.'
    );

    -- 4. FastAPI'ye modeli tetiklemesi için UUID'yi geri gönder
    RETURN v_yeni_talep_id;
END;
$$;