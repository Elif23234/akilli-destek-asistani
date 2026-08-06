import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getPersonelTaleplerim,
} from "../services/api";

import "./PersonelPaneli.css";

function PersonelPaneli() {
  const navigate = useNavigate();

  const [personel, setPersonel] =
    useState(null);

  const [talepler, setTalepler] =
    useState([]);

  const [aramaMetni, setAramaMetni] =
    useState("");

  const [durumFiltresi, setDurumFiltresi] =
    useState("tum");

  const [oncelikFiltresi, setOncelikFiltresi] =
    useState("tum");

  const [yukleniyor, setYukleniyor] =
    useState(true);

  const [hata, setHata] =
    useState("");
const [aktifMenu, setAktifMenu] =
  useState("atanan");

  useEffect(() => {
    async function talepleriGetir() {
      try {
        const sonuc =
          await getPersonelTaleplerim();

        setPersonel(
          sonuc.personel || null
        );

        setTalepler(
          sonuc.veri || []
        );
      } catch (error) {
        setHata(error.message);
      } finally {
        setYukleniyor(false);
      }
    }

    talepleriGetir();
  }, []);

  const filtrelenmisTalepler = useMemo(() => {
    const temizArama = aramaMetni
      .trim()
      .toLocaleLowerCase("tr-TR");

    return talepler.filter((talep) => {
      const aramayaUygun =
        !temizArama ||
        talep.talep_takip_no
          ?.toLocaleLowerCase("tr-TR")
          .includes(temizArama) ||
        talep.talep_baslik
          ?.toLocaleLowerCase("tr-TR")
          .includes(temizArama) ||
        talep.talep_gonderen_ad_soyad
          ?.toLocaleLowerCase("tr-TR")
          .includes(temizArama);

      const durumaUygun =
        durumFiltresi === "tum" ||
        talep.talep_durum === durumFiltresi;

      const onceligeUygun =
        oncelikFiltresi === "tum" ||
        talep.yz_oncelik_seviyesi ===
          oncelikFiltresi;

      return (
        aramayaUygun &&
        durumaUygun &&
        onceligeUygun
      );
    });
  }, [
    talepler,
    aramaMetni,
    durumFiltresi,
    oncelikFiltresi,
  ]);

  const toplamTalep = talepler.length;

  const onayBekleyenTalep = talepler.filter(
    (talep) =>
      talep.talep_durum === "onay_bekliyor"
  ).length;

  const yuksekOncelikliTalep = talepler.filter(
    (talep) =>
      talep.yz_oncelik_seviyesi === "Yüksek" ||
      talep.yz_oncelik_seviyesi === "Kritik"
  ).length;

  const cozulenTalep = talepler.filter(
    (talep) =>
      talep.talep_durum === "cozuldu"
  ).length;

  function cikisYap() {
    sessionStorage.removeItem(
      "personel_token"
    );

    sessionStorage.removeItem(
      "personel_bilgisi"
    );

    navigate(
      "/personel-giris",
      {
        replace: true,
      }
    );
  }

  function filtreleriTemizle() {
    setAramaMetni("");
    setDurumFiltresi("tum");
    setOncelikFiltresi("tum");
  }
function paneliGoster() {
  setAktifMenu("panel");
  setAramaMetni("");
  setDurumFiltresi("tum");
  setOncelikFiltresi("tum");

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

function atananTalepleriGoster() {
  setAktifMenu("atanan");
  setAramaMetni("");
  setDurumFiltresi("tum");
  setOncelikFiltresi("tum");

  document
    .querySelector(".personel-talep-bolumu")
    ?.scrollIntoView({
      behavior: "smooth",
    });
}

function onayBekleyenleriGoster() {
  setAktifMenu("onay");
  setAramaMetni("");
  setDurumFiltresi("onay_bekliyor");
  setOncelikFiltresi("tum");

  document
    .querySelector(".personel-talep-bolumu")
    ?.scrollIntoView({
      behavior: "smooth",
    });
}

function tamamlananTalepleriGoster() {
  setAktifMenu("tamamlanan");
  setAramaMetni("");
  setDurumFiltresi("cozuldu");
  setOncelikFiltresi("tum");

  document
    .querySelector(".personel-talep-bolumu")
    ?.scrollIntoView({
      behavior: "smooth",
    });
}

function istatistikleriGoster() {
  setAktifMenu("istatistikler");

  document
    .querySelector(".personel-istatistikler")
    ?.scrollIntoView({
      behavior: "smooth",
    });
}

function profiliGoster() {
  setAktifMenu("profil");

  document
    .querySelector(".personel-sidebar-alt")
    ?.scrollIntoView({
      behavior: "smooth",
    });
}
  function durumMetniOlustur(durum) {
    const durumlar = {
      onay_bekliyor: "Onay Bekliyor",
      inceleniyor: "İnceleniyor",
      musteri_yaniti_bekleniyor:
        "Müşteri Yanıtı Bekleniyor",
      otomatik_yanitlandi:
        "Otomatik Yanıtlandı",
      cozuldu: "Çözüldü",
      acik: "Açık",
    };

    return durumlar[durum] || durum;
  }

  function tarihBicimlendir(tarih) {
    if (!tarih) {
      return "Belirtilmemiş";
    }

    return new Date(tarih).toLocaleString(
      "tr-TR",
      {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }
    );
  }

  if (yukleniyor) {
    return (
      <div className="personel-yukleme">
        <div className="personel-yukleme-karti">
          <div className="personel-yukleme-ikonu">
            ⏳
          </div>

          <h2>
            Personel paneli yükleniyor...
          </h2>
        </div>
      </div>
    );
  }

  if (hata) {
    return (
      <div className="personel-yukleme">
        <div className="personel-hata-karti">
          <div className="personel-yukleme-ikonu">
            ⚠️
          </div>

          <h2>Bir sorun oluştu</h2>

          <p>{hata}</p>

          <button
            type="button"
            onClick={cikisYap}
          >
            Giriş ekranına dön
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="personel-paneli">
      <aside className="personel-sidebar">
        <div className="personel-logo-alani">
          <div className="personel-logo-ikonu">
            🤖
          </div>

          <div>
            <strong>
              Akıllı Destek
            </strong>

            <span>
              Asistanı
            </span>
          </div>
        </div>

        <nav className="personel-menu">
  <button
    type="button"
    className={`personel-menu-link ${
      aktifMenu === "panel" ? "aktif" : ""
    }`}
    onClick={paneliGoster}
  >
    <span>⌂</span>
    Panelim
  </button>

  <button
    type="button"
    className={`personel-menu-link ${
      aktifMenu === "atanan" ? "aktif" : ""
    }`}
    onClick={atananTalepleriGoster}
  >
    <span>▣</span>
    Bana Atanan Talepler
  </button>

  <button
    type="button"
    className={`personel-menu-link ${
      aktifMenu === "onay" ? "aktif" : ""
    }`}
    onClick={onayBekleyenleriGoster}
  >
    <span>⌛</span>
    Onay Bekleyen Talepler
  </button>

  <button
    type="button"
    className={`personel-menu-link ${
      aktifMenu === "tamamlanan" ? "aktif" : ""
    }`}
    onClick={tamamlananTalepleriGoster}
  >
    <span>✓</span>
    Tamamlanan Talepler
  </button>

  <button
    type="button"
    className={`personel-menu-link ${
      aktifMenu === "istatistikler" ? "aktif" : ""
    }`}
    onClick={istatistikleriGoster}
  >
    <span>▥</span>
    İstatistikler
  </button>

  <button
    type="button"
    className={`personel-menu-link ${
      aktifMenu === "profil" ? "aktif" : ""
    }`}
    onClick={profiliGoster}
  >
    <span>◉</span>
    Profilim
  </button>
</nav>

        <div className="personel-sidebar-alt">
          <div className="personel-mini-profil">
            <div className="personel-avatar">
              {personel?.kullanici_ad_soyad
                ?.charAt(0)
                .toLocaleUpperCase("tr-TR") ||
                "P"}
            </div>

            <div>
              <strong>
                {personel?.kullanici_ad_soyad ||
                  "Personel"}
              </strong>

              <span>
                Destek Personeli
              </span>

              <small>
                <i></i>
                Çevrimiçi
              </small>
            </div>
          </div>

          <button
            type="button"
            className="personel-cikis-butonu"
            onClick={cikisYap}
          >
            <span>↪</span>
            Çıkış Yap
          </button>
        </div>
      </aside>

      <div className="personel-ana-alan">
        <header className="personel-ust-bar">
          <div className="personel-ust-baslik">
            <span className="personel-menu-ikonu">
              ☰
            </span>

            <h1>
              Personel Paneli
            </h1>
          </div>

          <div className="personel-ust-profil">
            <div className="bildirim-alani">
              🔔
              <span>2</span>
            </div>

            <div className="ust-avatar">
              {personel?.kullanici_ad_soyad
                ?.charAt(0)
                .toLocaleUpperCase("tr-TR") ||
                "P"}
            </div>

            <div>
              <strong>
                {personel?.kullanici_ad_soyad ||
                  "Personel"}
              </strong>

              <span>
                Destek Personeli
              </span>
            </div>
          </div>
        </header>

        <main className="personel-icerik">
          <section className="personel-istatistikler">
            <article className="personel-istatistik-karti mor">
              <div className="istatistik-ikonu">
                📋
              </div>

              <div>
                <strong>{toplamTalep}</strong>
                <h3>Toplam Talep</h3>
                <p>
                  Bana atanan toplam talep
                </p>
              </div>
            </article>

            <article className="personel-istatistik-karti turuncu">
              <div className="istatistik-ikonu">
                🕒
              </div>

              <div>
                <strong>
                  {onayBekleyenTalep}
                </strong>

                <h3>
                  Onay Bekleyen
                </h3>

                <p>
                  Yanıt bekleyen talepler
                </p>
              </div>
            </article>

            <article className="personel-istatistik-karti pembe">
              <div className="istatistik-ikonu">
                ❗
              </div>

              <div>
                <strong>
                  {yuksekOncelikliTalep}
                </strong>

                <h3>
                  Yüksek Öncelikli
                </h3>

                <p>
                  Öncelikli müdahale gerekenler
                </p>
              </div>
            </article>

            <article className="personel-istatistik-karti yesil">
              <div className="istatistik-ikonu">
                ✅
              </div>

              <div>
                <strong>
                  {cozulenTalep}
                </strong>

                <h3>
                  Çözülen Talepler
                </h3>

                <p>
                  Çözüme kavuşturulanlar
                </p>
              </div>
            </article>
          </section>

          <section className="personel-talep-bolumu">
            <div className="personel-talep-basligi">
              <div>
                <span>
                  PERSONEL İŞ LİSTESİ
                </span>

                <h2>
                  Bana Atanan Talepler
                </h2>
              </div>
            </div>

            <div className="personel-filtreler">
              <div className="personel-arama">
                <span>⌕</span>

                <input
                  type="text"
                  value={aramaMetni}
                  onChange={(event) =>
                    setAramaMetni(
                      event.target.value
                    )
                  }
                  placeholder={
                    "Takip no, başlık veya müşteri ara..."
                  }
                />
              </div>

              <select
                value={durumFiltresi}
                onChange={(event) =>
                  setDurumFiltresi(
                    event.target.value
                  )
                }
              >
                <option value="tum">
                  Durum: Tümü
                </option>

                <option value="onay_bekliyor">
                  Onay Bekliyor
                </option>

                <option value="inceleniyor">
                  İnceleniyor
                </option>

                <option value="musteri_yaniti_bekleniyor">
                  Müşteri Yanıtı Bekleniyor
                </option>

                <option value="cozuldu">
                  Çözüldü
                </option>
              </select>

              <select
                value={oncelikFiltresi}
                onChange={(event) =>
                  setOncelikFiltresi(
                    event.target.value
                  )
                }
              >
                <option value="tum">
                  Öncelik: Tümü
                </option>

                <option value="Kritik">
                  Kritik
                </option>

                <option value="Yüksek">
                  Yüksek
                </option>

                <option value="Orta">
                  Orta
                </option>

                <option value="Düşük">
                  Düşük
                </option>
              </select>

              <button
                type="button"
                className="filtre-temizle"
                onClick={filtreleriTemizle}
                title="Filtreleri temizle"
              >
                ↻
              </button>
            </div>

            {filtrelenmisTalepler.length === 0 ? (
              <div className="personel-bos-durum">
                <div>📭</div>

                <h3>
                  Talep bulunamadı
                </h3>

                <p>
                  Seçilen filtrelere uygun
                  bir talep bulunmuyor.
                </p>
              </div>
            ) : (
              <div className="personel-talep-listesi">
                {filtrelenmisTalepler.map(
                  (talep) => (
                    <article
                      className={`personel-talep-karti oncelik-${(
                        talep.yz_oncelik_seviyesi ||
                        "belirsiz"
                      ).toLocaleLowerCase(
                        "tr-TR"
                      )}`}
                      key={talep.talep_id}
                    >
                      <div className="talep-sol-alan">
                        <span className="talep-takip-no">
                          {talep.talep_takip_no}
                        </span>

                        <span
                          className={`talep-oncelik-rozet oncelik-${(
                            talep.yz_oncelik_seviyesi ||
                            "belirsiz"
                          ).toLocaleLowerCase(
                            "tr-TR"
                          )}`}
                        >
                          ↑{" "}
                          {talep.yz_oncelik_seviyesi ||
                            "Belirsiz"}
                        </span>

                        <div className="talep-musteri">
                          <span>
                            👤{" "}
                            {talep.talep_gonderen_ad_soyad}
                          </span>

                          <span>
                            ✉{" "}
                            {talep.talep_gonderen_eposta}
                          </span>
                        </div>
                      </div>

                      <div className="talep-orta-alan">
                        <h3>
                          {talep.talep_baslik}
                        </h3>

                        <p>
                          {talep.talep_ham_icerik}
                        </p>

                        <div className="talep-meta">
                          <div>
                            <span>● Durum</span>

                            <strong>
                              {durumMetniOlustur(
                                talep.talep_durum
                              )}
                            </strong>
                          </div>

                          <div>
                            <span>▣ Oluşturulma</span>

                            <strong>
                              {tarihBicimlendir(
                                talep.talep_olusturulma_tarihi
                              )}
                            </strong>
                          </div>

                          <div>
                            <span>◷ Güncellenme</span>

                            <strong>
                              {tarihBicimlendir(
                                talep.talep_guncellenme_tarihi
                              )}
                            </strong>
                          </div>
                        </div>
                      </div>

                      <div className="talep-islemler">
                          <button
  type="button"
  className="detay-butonu"
  onClick={() =>
    navigate(
      `/personel-talep/${talep.talep_id}`
    )
  }
>
  ◉ Detayı Gör
</button>

                         <button
  type="button"
  className="cevap-butonu"
  onClick={() =>
    navigate(
      `/personel-talep/${talep.talep_id}`
    )
  }
>
  ✈ Cevap Yaz
</button>
                      </div>
                    </article>
                  )
                )}
              </div>
            )}

            <div className="personel-liste-alt">
              <span>
                Toplam{" "}
                {filtrelenmisTalepler.length} talep
              </span>
            </div>
          </section>
        </main>

        <footer className="personel-footer">
          © 2026 Akıllı Destek Asistanı —
          Tüm hakları saklıdır.
        </footer>
      </div>
    </div>
  );
}

export default PersonelPaneli;