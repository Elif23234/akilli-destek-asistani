import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import {
  musteriCozumOnayiGonder,
} from "../services/api";

function MusteriOnayi() {
  const [searchParams] = useSearchParams();

  const [yukleniyor, setYukleniyor] =
    useState(true);

  const [mesaj, setMesaj] = useState("");
  const [hata, setHata] = useState("");

  useEffect(() => {
    async function onayiGonder() {
      const talepId = (
        searchParams.get("talep_id") || ""
      ).trim();

      const sonuc = (
        searchParams.get("sonuc") || ""
      )
        .trim()
        .toLocaleLowerCase("tr-TR");

      if (!talepId) {
        setHata(
          "Talep bilgisi bulunamadı."
        );
        setYukleniyor(false);
        return;
      }

      if (
        sonuc !== "evet" &&
        sonuc !== "hayir"
      ) {
        setHata(
          "Geçersiz onay seçeneği."
        );
        setYukleniyor(false);
        return;
      }

      const cozulduMu =
        sonuc === "evet";

      console.log(
        "Talep ID:",
        talepId
      );

      console.log(
        "URL sonucu:",
        sonuc
      );

      console.log(
        "Backend'e gönderilen cozuldu_mu:",
        cozulduMu
      );

      try {
        const cevap =
          await musteriCozumOnayiGonder({
            talepId: talepId,
            cozulduMu: cozulduMu,
          });

        setMesaj(
          cevap.mesaj ||
            "Geri bildiriminiz alındı."
        );
      } catch (error) {
        setHata(
          error.message
        );
      } finally {
        setYukleniyor(false);
      }
    }

    onayiGonder();
  }, [searchParams]);

  if (yukleniyor) {
    return (
      <section>
        <h2>
          Geri bildiriminiz işleniyor...
        </h2>
      </section>
    );
  }

  if (hata) {
    return (
      <section>
        <h2>Bir sorun oluştu</h2>
        <p>{hata}</p>
      </section>
    );
  }

  return (
    <section>
      <h2>Teşekkür ederiz</h2>
      <p>{mesaj}</p>
    </section>
  );
}

export default MusteriOnayi;