# 🏟 ArenaBot — Stadion Joylash va Murojaatlar Boti

Ushbu Telegram bot **Python (aiogram 3.x)** va **SQLite3** yordamida stadion egalaridan arizalar qabul qilish, foydalanuvchilarning taklif va shikoyatlarini yig'ish, ularga admin orqali javob qaytarish hamda tez-tez so'raladigan savollarga (FAQ) javob berish uchun to'liq ishlab chiqilgan.

---

## 🚀 Imkoniyatlar va Funksiyalar

1. **Stadion joylash arizasi (6 ta majburiy parametr bo'yicha FSM):**
   - 📍 **1-qadam:** Viloyat tanlash (12 ta viloyat + Toshkent sh. + Qoraqalpog'iston R. 2 ustunli Inline menyuda);
   - 🗺 **2-qadam:** Aniq manzil, stadion nomi va mo'ljal;
   - 📞 **3-qadam:** Mas'ul shaxs telefon raqami (kontakt yuborish yoki +998... formatida qo'lda kiritish);
   - 📸 **4-qadam:** Stadion rasmlari — **kamida 2 ta, 10 tagacha** (albom yoki bittalab yuborish mumkin, 2+ ta rasm yuklangach «✅ Rasmlarni yakunlash» tugmasi chiqadi);
   - 💰 **5-qadam:** Soatlik ijara narxi;
   - 🤝 **6-qadam:** Zaklad (avans) olinishi yoki olinmasligi;
   - 🖼 **Yakuniy tekshirish (Preview):** Yuklangan barcha rasmlar albomi va 6 ta parametr aks etgan chiroyli kartochka orqali arizani tasdiqlash, qaytadan to'ldirish yoki bekor qilish.

2. **Taklif va shikoyatlar tizimi:**
   - 💡 Taklif, ⚠️ Shikoyat yoki ❓ Savol turlaridan birini tanlash;
   - Telefon raqamni kiritish yoki «➡️ Raqamsiz davom etish»;
   - Murojaat matni va ixtiyoriy skrinshot/rasm yuklash;
   - Murojaat saqlangach, barcha adminlarga tezkor yetkaziladi;
   - Admin xabar ostidagi **«✍️ Javob yozish»** tugmasini bosib javob yozsa, foydalanuvchiga to'g'ridan-to'g'ri yetkaziladi.

3. **Foydalanuvchi qulayliklari:**
   - `📋 Mening arizalarim` — foydalanuvchining arizalari ro'yxati va ularning statusi (`⏳ Ko'rib chiqilmoqda`, `✅ Tasdiqlangan`, `❌ Rad etilgan`);
   - `❓ Ko'p beriladigan savollar` — tezkor FAQ tugmalari;
   - **Avto-javoblar (Auto-reply):** Chatga "stadion", "narx", "qo'shish", "shikoyat", "taklif" kabi so'zlar yozilganda, bot foydalanuvchini kerakli menyuga yo'naltiradi;
   - `❌ Bekor qilish` — istalgan qadamda jarayonni bekor qilib, asosiy menyuga qaytish imkoniyati.

4. **Admin Paneli (`/admin`) va Moderatsiya:**
   - Har bir tushgan stadion arizasi adminlarga rasmlar albomi va `✅ Tasdiqlash` hamda `❌ Rad etish` tugmalari bilan keladi;
   - Tasdiqlanganda yoki rad etilganda ariza egasiga avtomatik bildirishnoma boradi;
   - `/admin` buyrug'i orqali arizalar va murojaatlarning umumiy statistikasi, kutilayotgan arizalar va yangi murojaatlar ro'yxatini ko'rish.

---

## 📁 Loyiha Strukturasi

```
Arenabot/
│
├── .env                  # Maxfiy tokenlar va admin ID lari
├── .env.example          # Namuna konfiguratsiya fayli
├── requirements.txt      # Kutubxonalar ro'yxati (aiogram>=3.4.0, python-dotenv)
├── config.py             # Sozlamalar va o'zgaruvchilarni yuklash
├── database.py           # SQLite3 bazasi bilan ishlash (stadiums va feedbacks jadvallari)
├── main.py               # Botni ishga tushiruvchi asosiy fayl
│
├── keyboards/
│   ├── user_kb.py        # Foydalanuvchi klaviaturalari (asosiy, hududlar, zaklad, FAQ)
│   └── admin_kb.py       # Admin klaviaturalari (moderatsiya, javob yozish)
│
├── states/
│   ├── stadium_state.py  # Stadion anketasi FSM holatlari
│   ├── feedback_state.py # Taklif/shikoyat FSM holatlari
│   └── admin_state.py    # Admin javob yozish FSM holati
│
└── handlers/
    ├── common.py         # /start, /cancel, FAQ va kalit so'zlar avto-javoblari
    ├── stadium.py        # Stadion arizasini to'ldirish va "Mening arizalarim"
    ├── feedback.py       # Taklif va shikoyatlarni qabul qilish
    └── admin.py          # /admin buyrug'i, arizalarni tasdiqlash/rad etish, javob yozish
```

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

### 2. `.env` faylini sozlash:
Loyiha papkasidagi `.env` faylini oching va ma'lumotlaringizni kiriting:
```ini
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
ADMIN_IDS=123456789,987654321
GROUP_ID=-1001234567890
DB_PATH=stadion_bot.db
```
*(Eslatma:*
- *O'zingizning shaxsiy Telegram ID raqamingizni `@userinfobot` orqali bilib olishingiz mumkin;*
- *Telegram guruh ID sini bilish uchun botni guruhga qo'shib, admin qiling va `@RawDataBot` yoki guruh xabarini yo'naltirish orqali guruh ID sini (odatda `-100...` bilan boshlanadi) oling).*

### 3. Botni ishga tushirish:
```bash
python main.py
```
yoki (Windows da):
```bash
py -3.12 main.py
```
