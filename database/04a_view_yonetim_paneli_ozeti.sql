CREATE OR REPLACE VIEW vw_yonetim_paneli_ozeti AS
SELECT
    t.talep_takip_no,
    t.talep_baslik,
    k.kategori_ad,
    yz.yz_oncelik_seviyesi,
    yz.yz_duygu_durumu,
    yz.yz_ozet,
    t.talep_durum,
    t.talep_olusturulma_tarihi
FROM
    talepler t
LEFT JOIN
    kategoriler k ON t.talep_kategori_id = k.kategori_id
LEFT JOIN
    yz_analizleri yz ON t.talep_id = yz.yz_talep_id
WHERE
    -- Yönetim ekranında yalnızca açık talepler gösterilir
    t.talep_durum != 'kapali'
ORDER BY
    -- Öncelik seviyesine göre sıralama yap; acil talepler en üste gelir
    CASE yz.yz_oncelik_seviyesi
        WHEN 'Acil' THEN 1
        WHEN 'Yüksek' THEN 2
        WHEN 'Orta' THEN 3
        WHEN 'Düşük' THEN 4
        ELSE 5
    END,
    t.talep_olusturulma_tarihi ASC;