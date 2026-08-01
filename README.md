# 🤖 Akıllı Destek Asistanı

Yapay zekâ destekli müşteri destek otomasyon sistemi.

Bu proje, müşteri destek taleplerini yapay zekâ ile analiz eden, benzer geçmiş talepleri RAG (Retrieval-Augmented Generation) yöntemiyle bulan, kritik talepleri otomatik olarak ilgili personele yönlendiren ve yönetici paneli üzerinden tüm süreci yönetebilen uçtan uca bir destek otomasyon sistemidir.

---

# 🚀 Projenin Amacı

Müşteri destek ekiplerinin yoğun iş yükünü azaltmak amacıyla;

- Gelen destek taleplerini otomatik analiz etmek
- Talepleri kategorilere ayırmak
- Öncelik seviyesini belirlemek
- Duygu analizini yapmak
- Benzer geçmiş talepleri bulmak
- Kritik taleplerde ilgili personeli anında bilgilendirmek
- Personelin AI önerisini kontrol ederek müşteriye hızlı cevap göndermesini sağlamak

amaçlanmıştır.

---

# ✨ Temel Özellikler

✅ Destek talebi oluşturma

✅ PostgreSQL veritabanına kayıt

✅ Yapay zekâ ile otomatik analiz

- AI özeti
- Kategori belirleme
- Öncelik belirleme
- Duygu analizi
- Öncelik gerekçesi oluşturma

✅ pgvector tabanlı RAG benzer talep arama

✅ Yönetici paneli

✅ Dashboard istatistikleri

- Toplam talep
- Açık talepler
- Kritik talepler
- Son 24 saat
- Ortalama yanıt süresi
- Kategori dağılımı

✅ JWT tabanlı yönetici girişi

✅ SMTP ile e-posta gönderimi

✅ Telegram kritik bildirim sistemi

---

# 🏗 Sistem Mimarisi

```text
                    Müşteri

                       │

                       ▼

             React Talep Formu

                       │

                       ▼

                FastAPI Backend

                       │

        ┌──────────────┴──────────────┐

        ▼                             ▼

 PostgreSQL                    AI Motoru

                                     │

                                     ▼

               ┌────────────────────────────┐

               │                            │

               ▼                            ▼

          Kategori                     Duygu

               │

               ▼

         Öncelik Analizi

               │

               ▼

            AI Özeti

               │

               ▼

         pgvector / RAG

               │

               ▼

        Dashboard Paneli

               │

        ┌──────┴────────┐

        ▼               ▼

 Telegram         SMTP Mail
```

---

# 🧠 Yapay Zekâ Özellikleri

Sistem LLM kullanarak her destek talebi için;

- Talep özeti oluşturur
- Kategori belirler
- Öncelik seviyesi belirler
- Duygu analizi yapar
- Öncelik gerekçesi üretir

Kritik öncelikli talepler otomatik olarak personel incelemesine yönlendirilir.

---

# 🔍 RAG Sistemi

Sistem pgvector kullanarak geçmiş destek taleplerinin embedding vektörlerini oluşturur.

Yeni gelen talep ile geçmiş talepler arasında semantik benzerlik hesaplanır.

Böylece personel benzer geçmiş çözümleri görebilir.

---

# 📊 Dashboard

Dashboard üzerinden;

- Toplam destek talepleri
- Açık talepler
- Kritik talepler
- Son 24 saatte gelen talepler
- Ortalama yanıt süresi
- Yapay zekâ tarafından analiz edilen talepler
- Kategori dağılımı

takip edilebilir.

---

# 📧 SMTP Bildirim Sistemi

Personel, AI tarafından hazırlanan önerilen cevabı inceleyebilir.

Onayladıktan sonra cevap SMTP üzerinden müşteriye gönderilir.

---

# 📲 Telegram Bildirim Sistemi

Yapay zekâ kritik öncelikli bir destek talebi tespit ettiğinde;

- Talep otomatik olarak inceleniyor durumuna alınır.
- Telegram üzerinden ilgili personele bildirim gönderilir.

---

# 🛠 Kullanılan Teknolojiler

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- JWT Authentication
- SMTP
- Telegram Bot API

## Frontend

- React
- Vite
- React Router
- CSS

## AI

- LLM
- Prompt Engineering
- Embedding
- RAG (Retrieval-Augmented Generation)

---

# 📁 Proje Yapısı

```text
Akilli-Destek-Asistani/

│

├── backend/

├── frontend/

├── ai_motoru/

├── veri_seti/

├── docker-compose.yml

└── README.md
```

---

# ⚙ Kurulum

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 🔐 Ortam Değişkenleri

```
OPENAI_API_KEY=

DATABASE_URL=

JWT_SECRET_KEY=

SMTP_MAIL=

SMTP_PASSWORD=

BOT_TOKEN=

CHAT_ID=
```

---

# 📸 Ekran Görüntüleri

- Dashboard

- Talep Listesi

- Talep Detayı

- AI Analizi

- RAG Sonuçları

- Swagger API

- Telegram Bildirimi

- SMTP Mail

---

# 📌 Gelecek Çalışmalar

- Gerçek e-posta sistemleri ile entegrasyon

- Çoklu personel desteği

- Mobil uygulama

- Gerçek zamanlı WebSocket bildirimleri

- Performans analizi ve raporlama

---

# 👨‍💻 Geliştirici

Elif Cankara

Yönetim Bilişim Sistemleri

Fırat Üniverstesi