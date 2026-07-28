from ai_motoru.llm import talebi_llm_ile_analiz_et
from ai_motoru.models import AnalizIstegi, AnalizSonucu
from ai_motoru.rag import rag_baglami_hazirla


def talebi_analiz_et(analiz_istegi: AnalizIstegi) -> AnalizSonucu:

    benzer_talepler = []

    for talep in analiz_istegi.benzer_talepler:
        benzer_talepler.append(talep.model_dump())

    rag_baglami = rag_baglami_hazirla(
        benzer_talepler
    )

    llm_sonucu = talebi_llm_ile_analiz_et(
        baslik=analiz_istegi.baslik,
        icerik=analiz_istegi.icerik,
        rag_baglami=rag_baglami
    )

    analiz_sonucu = AnalizSonucu.model_validate(
        llm_sonucu
    )

    return analiz_sonucu