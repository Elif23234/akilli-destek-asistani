-- YZ analizi sonucunda acil olarak işaretlenen bir talep için bildirim oluşturan trigger fonksiyonu
CREATE OR REPLACE FUNCTION fn_acil_durum_bildirimi()
RETURNS TRIGGER AS $$
BEGIN
    -- Eğer analiz sonucu acil öncelik seviyesine sahipse, kullanıcıya bildirimi tetikle
    IF NEW.yz_oncelik_seviyesi = 'Acil' THEN
        -- Bildirim kuyruğuna yeni bir kayıt ekleyerek mesajın beklemede olduğunu belirt
        INSERT INTO bildirim_kayitlari (
            bildirim_talep_id,
            bildirim_kanal,
            bildirim_hash,
            bildirim_durum
        ) VALUES (
            NEW.yz_talep_id,
            'telegram', -- Varsayılan bildirim kanalı
            md5(NEW.yz_talep_id::TEXT || CURRENT_TIMESTAMP::TEXT), -- Her kayıt için benzersiz bir kimlik üret
            'bekliyor'
        );

        -- Ana talebin bildirildi olarak işaretlenmesini sağlayarak takip sürecini başlat
        UPDATE talepler
        SET talep_bildirildi = TRUE
        WHERE talep_id = NEW.yz_talep_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- yz_analizleri tablosuna her INSERT veya UPDATE sonrası bu fonksiyonun çalışmasını sağlar
CREATE TRIGGER trg_yz_analiz_acil_bildirim
AFTER INSERT OR UPDATE ON yz_analizleri
FOR EACH ROW
EXECUTE FUNCTION fn_acil_durum_bildirimi();