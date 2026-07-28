def rag_baglami_hazirla(benzer_talepler: list[dict]) -> str:
    if not benzer_talepler:
        return "Geçmişte çözülmüş benzer bir destek talebi bulunamadı."

    baglam = "Geçmişte çözülmüş benzer destek talepleri:\n\n"

    sira_no = 1

    for talep in benzer_talepler:
        baslik = talep.get("baslik", "Başlık bulunamadı")
        icerik = talep.get("icerik", "İçerik bulunamadı")
        cozum = talep.get("cozum", "Çözüm bilgisi bulunamadı")

        baglam = baglam + f"Benzer Talep {sira_no}\n"
        baglam = baglam + f"Başlık: {baslik}\n"
        baglam = baglam + f"İçerik: {icerik}\n"
        baglam = baglam + f"Çözüm: {cozum}\n\n"

        sira_no = sira_no + 1

    return baglam