-- 04e_view_incelenen_talepler.sql
CREATE OR REPLACE VIEW vw_incelenen_talepler AS
SELECT
    t.talep_id,
    t.talep_takip_no,
    t.talep_baslik,
    t.talep_ham_icerik,
    k.kategori_ad,
    k.kategori_departman,
    yz.yz_guven_skoru,
    yz.yz_ozet,
    yz.yz_musteri_cevabi AS ai_taslak_yanit, -- YZ'nin düşük güvenle de olsa çıkardığı taslak
    yz.yz_cozum_onerisi,
    t.talep_olusturulma_tarihi
FROM talepler t
JOIN kategoriler k ON t.talep_kategori_id = k.kategori_id
JOIN yz_analizleri yz ON t.talep_id = yz.yz_talep_id
WHERE t.talep_durum = 'inceleniyor'
ORDER BY t.talep_olusturulma_tarihi ASC;