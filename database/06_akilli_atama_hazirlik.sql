-- Personellerin bağlı olduğu departmanı tutar.
ALTER TABLE kullanicilar
ADD COLUMN IF NOT EXISTS kullanici_departman
VARCHAR(100);

-- Personel departmanına göre aramaları hızlandırır.
CREATE INDEX IF NOT EXISTS
idx_kullanicilar_departman
ON kullanicilar(kullanici_departman);