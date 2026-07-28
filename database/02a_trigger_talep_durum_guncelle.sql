-- Güncelleme Tarihi Otomasyonu
CREATE OR REPLACE FUNCTION fn_talep_guncellenme_tarihi()
RETURNS TRIGGER AS $$
BEGIN
    NEW.talep_guncellenme_tarihi = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_talepler_guncelleme_tarihi ON talepler;
CREATE TRIGGER trg_talepler_guncelleme_tarihi
BEFORE UPDATE ON talepler
FOR EACH ROW
EXECUTE FUNCTION fn_talep_guncellenme_tarihi();