CREATE OR REPLACE VIEW vw_kategori_istatistikleri AS
SELECT
    k.kategori_ad,
    COUNT(t.talep_id) AS toplam_talep,
    SUM(CASE WHEN t.talep_durum = 'kapali' THEN 1 ELSE 0 END) AS cozulmus_talep,
    SUM(CASE WHEN t.talep_durum != 'kapali' THEN 1 ELSE 0 END) AS bekleyen_talep,
    SUM(CASE WHEN yz.yz_oncelik_seviyesi = 'Acil' THEN 1 ELSE 0 END) AS acil_talep_sayisi
FROM
    kategoriler k
LEFT JOIN
    talepler t ON k.kategori_id = t.talep_kategori_id
LEFT JOIN
    yz_analizleri yz ON t.talep_id = yz.yz_talep_id
GROUP BY
    k.kategori_ad
ORDER BY
    -- En çok bekleyen talebe sahip kategoriler önce görünür
    bekleyen_talep DESC;