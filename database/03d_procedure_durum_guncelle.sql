CREATE OR REPLACE PROCEDURE sp_talep_durum_guncelle(
    p_talep_id UUID,
    p_kullanici_id UUID, -- İşlemi yapan yetkili/temsilci
    p_yeni_durum VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_eski_durum VARCHAR(50);
BEGIN
    -- 1. Loga yazabilmek için talebin şu anki (eski) durumunu öğreniyoruz (durum -> talep_durum)
    SELECT talep_durum INTO v_eski_durum 
    FROM talepler 
    WHERE talep_id = p_talep_id;

    -- Eğer durum zaten aynıysa boş yere işlem yapmayı engellemek için küçük bir kontrol:
    IF v_eski_durum = p_yeni_durum THEN
        RETURN; -- Hiçbir şey yapmadan prosedürden çık
    END IF;

    -- 2. Talepler tablosunda durumu güncelle (durum -> talep_durum)
    UPDATE talepler 
    SET talep_durum = p_yeni_durum 
    WHERE talep_id = p_talep_id;

    -- 3. OTOMATİK İŞLEM KAYDI (Log) Eklemesi
    INSERT INTO islem_kayitlari (
        islem_talep_id, 
        islem_kullanici_id, 
        islem_tipi, 
        islem_eski_durum, 
        islem_yeni_durum, 
        islem_aciklama
    )
    VALUES (
        p_talep_id, 
        p_kullanici_id, 
        'DURUM_GÜNCELLEME', 
        v_eski_durum, 
        p_yeni_durum, 
        'Talep statüsü ' || v_eski_durum || ' durumundan ' || p_yeni_durum || ' durumuna alındı.'
    );
END;
$$;