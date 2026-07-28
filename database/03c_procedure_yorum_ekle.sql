CREATE OR REPLACE PROCEDURE sp_talebe_yorum_ekle(
    p_talep_id UUID,
    p_kullanici_id UUID,
    p_mesaj TEXT,
    p_yeni_durum VARCHAR DEFAULT NULL,
    p_islem_yapan_tipi VARCHAR DEFAULT 'personel' -- Seçenekler: 'musteri', 'personel', 'yz'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_mevcut_durum VARCHAR;
    v_guncel_durum VARCHAR;
    v_log_aciklamasi TEXT;
    v_ayni_mesaj_var_mi BOOLEAN;
BEGIN
    -- 1. Çift Kayıt (Duplicate) Kontrolü
    SELECT EXISTS (
        SELECT 1 FROM yorumlar 
        WHERE yorum_talep_id = p_talep_id AND yorum_mesaj = p_mesaj
    ) INTO v_ayni_mesaj_var_mi;

    IF v_ayni_mesaj_var_mi THEN
        RETURN; -- Aynı yorum zaten var, sistemi yormadan çık.
    END IF;

    -- 2. Mevcut Durumu Çek
    SELECT talep_durum INTO v_mevcut_durum FROM talepler WHERE talep_id = p_talep_id;
    v_guncel_durum := COALESCE(p_yeni_durum, v_mevcut_durum);

    -- 3. Durum Belirleme ve Otomasyon Mantığı (BEGIN İÇİNDE)
    IF p_islem_yapan_tipi = 'musteri' AND (v_mevcut_durum IN ('cozuldu', 'kapali', 'musteri_yaniti_bekleniyor')) THEN
        v_guncel_durum := 'acik';
        v_log_aciklamasi := 'Müşteri yeni yanıt verdi, talep otomatik olarak açık duruma getirildi.';
    ELSIF p_islem_yapan_tipi = 'yz' AND p_yeni_durum = 'cozuldu' THEN
        v_log_aciklamasi := 'YZ tarafından otomatik çözüldü.';
    ELSIF p_islem_yapan_tipi = 'yz' AND p_yeni_durum = 'musteri_yaniti_bekleniyor' THEN
        v_log_aciklamasi := 'YZ çözüm sundu, müşteriden onay bekleniyor.';
    ELSIF p_islem_yapan_tipi = 'personel' AND p_yeni_durum = 'beklemede' THEN
        v_log_aciklamasi := 'Personel tarafından beklemeye alındı.';
    ELSE
        v_log_aciklamasi := 'Talebe yeni bir yorum eklendi.';
    END IF;

    -- 4. Yorumu Kaydet
    INSERT INTO yorumlar (yorum_talep_id, yorum_kullanici_id, yorum_mesaj)
    VALUES (p_talep_id, p_kullanici_id, p_mesaj);

    -- 5. Durumu Güncelle (Eğer eski durumdan farklıysa)
    IF v_mevcut_durum IS DISTINCT FROM v_guncel_durum THEN
        UPDATE talepler 
        SET talep_durum = v_guncel_durum,
            talep_guncellenme_tarihi = CURRENT_TIMESTAMP
        WHERE talep_id = p_talep_id;
    END IF;

    -- 6. İşlem Kaydı (Log)
    INSERT INTO islem_kayitlari (
        islem_talep_id, islem_kullanici_id, islem_tipi, islem_eski_durum, islem_yeni_durum, islem_aciklama
    ) VALUES (
        p_talep_id, p_kullanici_id, 'YORUM_EKLENDİ', v_mevcut_durum, v_guncel_durum, v_log_aciklamasi
    );
END;
$$;