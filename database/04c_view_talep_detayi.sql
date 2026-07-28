CREATE OR REPLACE VIEW vw_talep_detayi AS
SELECT
    t.talep_id,
    t.talep_takip_no,
    t.talep_baslik,
    t.talep_ham_icerik,
    t.talep_durum,
    t.talep_kaynak,
    t.talep_gonderen_ad_soyad,
    t.talep_gonderen_eposta,
    k.kategori_ad,
    yz.yz_ozet,
    yz.yz_oncelik_seviyesi,
    yz.yz_duygu_durumu,
    yz.yz_guven_skoru,
    t.talep_olusturulma_tarihi,
    t.talep_guncellenme_tarihi
FROM
    talepler t
LEFT JOIN
    kategoriler k ON t.talep_kategori_id = k.kategori_id
LEFT JOIN
    yz_analizleri yz ON t.talep_id = yz.yz_talep_id;