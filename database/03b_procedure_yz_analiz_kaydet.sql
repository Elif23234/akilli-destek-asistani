CREATE OR REPLACE PROCEDURE sp_yz_analiz_kaydet(
    p_talep_id UUID,
    p_kategori_id INT,
    p_ozet TEXT,
    p_oncelik_skoru FLOAT,
    p_oncelik_seviyesi VARCHAR,
    p_duygu_durumu VARCHAR,
    p_guven_skoru FLOAT,
    p_cozum_onerisi TEXT,
    p_musteri_cevabi TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_mevcut_durum VARCHAR;
    v_is_riskli BOOLEAN := FALSE;
    v_yeni_durum VARCHAR;
BEGIN
    -- 1. Analizi Kaydet/Güncelle
    INSERT INTO yz_analizleri (
        yz_talep_id, yz_ozet, yz_oncelik_skoru, yz_oncelik_seviyesi, 
        yz_duygu_durumu, yz_guven_skoru, yz_cozum_onerisi, yz_musteri_cevabi
    ) VALUES (
        p_talep_id, p_ozet, p_oncelik_skoru, p_oncelik_seviyesi, 
        p_duygu_durumu, p_guven_skoru, p_cozum_onerisi, p_musteri_cevabi
    )
    ON CONFLICT (yz_talep_id) DO UPDATE 
    SET yz_ozet = EXCLUDED.yz_ozet,
        yz_oncelik_skoru = EXCLUDED.yz_oncelik_skoru,
        yz_oncelik_seviyesi = EXCLUDED.yz_oncelik_seviyesi,
        yz_duygu_durumu = EXCLUDED.yz_duygu_durumu,
        yz_guven_skoru = EXCLUDED.yz_guven_skoru,
        yz_cozum_onerisi = EXCLUDED.yz_cozum_onerisi,
        yz_musteri_cevabi = EXCLUDED.yz_musteri_cevabi;

    -- 2. Kategorinin Risk Durumunu Çek
    IF p_kategori_id IS NOT NULL THEN
        SELECT COALESCE(kategori_riskli, FALSE) INTO v_is_riskli 
        FROM kategoriler WHERE kategori_id = p_kategori_id;
    END IF;

    -- 3. ÜÇLÜ KARAR MEKANİZMASI
    IF p_guven_skoru >= 0.80 AND v_is_riskli = FALSE THEN
        v_yeni_durum := 'musteri_yaniti_bekleniyor'; -- Senaryo 1: Direkt Müşteriye
    ELSIF p_guven_skoru >= 0.80 AND v_is_riskli = TRUE THEN
        v_yeni_durum := 'onay_bekliyor'; -- Senaryo 2: Personel Onayına
    ELSE
        v_yeni_durum := 'inceleniyor'; -- Senaryo 3: AI Emin Değil, Personele İlet
    END IF;

    -- 4. Talebin Durumunu Güncelle
    SELECT talep_durum INTO v_mevcut_durum FROM talepler WHERE talep_id = p_talep_id;
    
    UPDATE talepler
    SET talep_kategori_id = p_kategori_id,
        talep_durum = v_yeni_durum,
        talep_guncellenme_tarihi = CURRENT_TIMESTAMP
    WHERE talep_id = p_talep_id;

    -- 5. İşlem Logu Tut (Eğer durum değiştiyse)
    IF v_mevcut_durum IS DISTINCT FROM v_yeni_durum THEN
        INSERT INTO islem_kayitlari (islem_talep_id, islem_tipi, islem_eski_durum, islem_yeni_durum, islem_aciklama)
        VALUES (p_talep_id, 'YZ_KARARI', v_mevcut_durum, v_yeni_durum, 'YZ analizine göre durum ataması yapıldı.');
    END IF;
END;
$$;