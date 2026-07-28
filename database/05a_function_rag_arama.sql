-- Vektörel arama yapan güncel fonksiyon
CREATE OR REPLACE FUNCTION fn_rag_vektor_arama(
    p_aranan_vektor vector(768),
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    talep_takip_no VARCHAR,
    talep_baslik VARCHAR,
    talep_icerik TEXT,
    cozum_durumu VARCHAR,
    benzerlik_skoru FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.talep_takip_no,
        t.talep_baslik,
        t.talep_ham_icerik AS talep_icerik,
        t.talep_durum AS cozum_durumu,
        -- pgvector <=> operatörü kosinüs mesafesini verir.
        -- 1'den çıkararak skoru yüksek olanın daha benzer olduğu bir yapı kuruyoruz.
        1 - (tv.vektor_deger <=> p_aranan_vektor) AS benzerlik_skoru
    FROM
        talep_vektorleri tv
    JOIN 
        talepler t ON tv.vektor_talep_id = t.talep_id
    ORDER BY
        tv.vektor_deger <=> p_aranan_vektor
    LIMIT p_limit;
END;
$$;