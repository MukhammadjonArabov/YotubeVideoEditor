# Musiqa: tinchlantiruvchi uzun musiqali videolar (20-30 daqiqa)

Uchinchi yo'nalish (2026-10-25, egasi talabi). Matnli tushuntirish yo'q: bitta musiqa, takrorlanadigan chiroyli video, kanal uchun uzoq tomosha vaqti.
Egasi bilan muloqot: o'zbekcha. Sahifa matnlari o'zbekcha. Sarlavha/tavsif: inglizcha yoki o'zbekcha, egasi aytganiga qarab (standart: inglizcha, global auditoriya).

## 1. Mahsulot

- **Musiqa:** ElevenLabs Music API bilan **3-4 daqiqalik** trek yaratiladi; u **yumshoq ulanish (crossfade) bilan takrorlanib 20-30 daqiqaga** uzaytiriladi.
  Faqat bitta trek uchun kredit ketadi; takrorlash bepul.
- **Ohang:** tabiat ovozlari (oqib turgan buloq, qushlar, shamol, yomg'ir), yumshoq pianino va pad, **ayol kishining so'zsiz, havodor ovozi (vocalise, hum, ohangli "aaa")**.
  Matn/qo'shiq so'zlari yo'q, barabanlar yo'q, keskin o'zgarish yo'q, hammasi uyqu va meditatsiya uchun.
- **Video:** egasi Google Flow'da 1-6 ta qisqa (8 soniyalik) klip yaratadi; ular uzluksiz takrorlanadigan blokka ulanadi. Tepada **Subscribe → Like** animatsiyasi
  boshida (~45 soniya) va har bir necha daqiqada (standart: har 5 daqiqada).
- **Davomiylik:** saytda egasi belgilaydi (5-180 daqiqa, odatda 20-30).

## 2. Ish tartibi

1. Men (Claude) g'oya/mavzuni aniqlayman: musiqa uchun inglizcha prompt (ElevenLabs), mos **Flow video promptlari** (musiqaning kayfiyatiga mos), sarlavha/tavsif/teg.
   Buyruq: `manage.py music_new ...` (loyihani va promptlarni saytga yuklaydi).
2. Saytda (`Musiqa` yo'nalishi → loyiha) egasi **musiqa promptini tahrirlashi**, **3-4 daqiqalik variantlar (take) yaratishi**, har birini **tinglashi** va eng yaxshisini tanlashi mumkin.
3. Har take uchun **avtomatik sifat tekshiruvi** (4-bo'lim) hisobot va ball beradi; men hisobotni ko'rib, yomon takelarni qayta yarataman (nazoratni men qilaman).
4. Egasi Flow'da klip yaratadi (promptlar saytda, nusxalash tugmasi bilan), kliplarni saytga yuklaydi, **video davomiyligini (daqiqa)** belgilaydi va **«Montajni boshlash»** ni bosadi.
5. Tayyor video saytda ko'rinadi; **nashr to'plami** (3 sarlavha, tavsif, teglar, 3 ta Flow preview prompti) ham shu yerda.

## 3. Musiqa prompti qoidalari (ElevenLabs Music)

- Inglizcha, aniq: janr/kayfiyat, asboblar, **vokal turi**, tabiat ovozi, tezlik (taxminan 50-60 BPM), "no drums, no sudden changes, seamless, consistent energy from start to end".
- Vokal: `wordless female vocals, airy soft vocalise, humming, no lyrics, no spoken words` (so'zsiz bo'lishi muhim: takrorlanganda zerikarli bo'lmasin va til/litsenziya muammosi bo'lmasin).
- Trek **bir xil energiyada** bo'lishi kerak (boshi va oxiri o'xshash): takrorlanganda ulanish sezilmasligi uchun. Kulminatsiya, finale, keskin tugash so'ralmaydi.
- Tabiat mavzulari (har loyiha bittasi): o'rmon buloq, tog' ko'li tong, yomg'irli kulba, tungi vodiy, okean qirg'og'i, bahorgi bog', qorli o'rmon, cho'l kechasi.

## 4. Sifat nazorati (avtomatik + men)

Har take uchun `services/music_qc.py` hisoblaydi va 0-100 ball beradi:

| Tekshiruv | Yaxshi | Nega |
|---|---|---|
| Umumiy balandlik (LUFS) | -23 ... -14 (maqsad ~-16) | YouTube me'yori; juda past/baland emas |
| Cho'qqi (true peak) | ≤ -1 dBFS | qirqilish (clipping) yo'q |
| Balandlik o'zgarishi (LRA) | ≤ 6 LU | tinch, "sakramaydigan" |
| Jimlik bo'shliqlari | trek o'rtasida >1,5 s jimlik yo'q | uzilish bo'lmasin |
| Boshi va oxiri o'xshashligi | energiya farqi ≤ 3 dB | takrorlash ulanishi sezilmasin |
| Davomiylik | 150-300 soniya | 3-4 daqiqa (5 daqiqagacha) |
| Spektral barqarorlik | keskin o'zgarishlar kam | uyqu musiqasi bir tekis |

- Men hisobotni o'qiyman: ball < 70 yoki «jiddiy» ogohlantirish bo'lsa, take rad etiladi va boshqa seed/prompt bilan qayta yaratiladi (kredit sarfini egasiga aytib turaman).
- Ayol vokali borligini va tabiiyligini ovozni **tinglab** egasi tasdiqlaydi (avtomatik baholash ishonchsiz); men esa ovoz xarakteristikalarini (spektr, balandlik) tekshiraman.
- Ulanish joyini tinglash tugmasi (takrorlash joyi atrofidagi 20 soniya) saytda bor.

## 5. Flow video promptlari qoidalari

- Musiqa kayfiyatiga to'liq mos (xuddi shu joy, vaqt, yorug'lik); har klip alohida, lekin bir uslubda (bir "dunyo").
- 8 soniya, **uzluksiz takrorlanishi mumkin**: kamera deyarli qimirlamaydi yoki juda sekin suzadi; boshi va oxiri o'xshash; tez harakat yo'q.
- Matn yo'q, logotip yo'q, odam yuzi yo'q (yoki uzoq siluet). Uslub: chiroyli, realistik yoki rassom chizgan animatsiya (egasi tanlaydi; standart: yumshoq "hand-painted animation").
- Har loyiha uchun 3-6 prompt: keng manzara, yaqin plan (suv/barg/qush), yorug'lik o'zgarishi, tungi variant.

## 6. Saytdagi imkoniyatlar (Musiqa yo'nalishi)

- Loyihalar ro'yxati va statistika (tayyor videolar soni, jami daqiqa).
- Loyiha sahifasi: musiqa prompti (tahrirlanadi), take'lar (har birini tinglash, ball va hisobot, tanlash/o'chirish), davomiylik, Subscribe/Like sozlamalari,
  Flow promptlari (tahrirlanadi, nusxalash), klip yuklash, montaj tugmasi, jarayon ko'rsatkichi, tayyor video (ijro va yuklab olish), nashr to'plami.
- Qo'shimcha: tayyor mp3 yuklash (boshqa joydan), take'larni solishtirish, takrorlash soni va umumiy davomiylik hisobi, maslahat ("20 daqiqa = trek N marta").

## 7. Cheklovlar va xavfsizlik

- **Pul:** ElevenLabs Music API **pullik reja** talab qiladi (bepul rejada «paid_plan_required»). Rejani egasi yoqadi; kredit sarfi haqida men oldindan aytaman, ruxsatsiz take yaratilmaydi.
- **Litsenziya:** ElevenLabs Music (pullik rejada) tijoriy foydalanishga ruxsat beradi deb e'lon qilingan; egasi o'z rejasining shartlarini tekshiradi. Boshqa kishi ovozi klonlanmaydi.
- **Monetizatsiya:** uzun takrorlanuvchi videolar YouTube'da "takrorlanuvchi/shablon kontent" deb baholanishi mumkin. Kamaytirish uchun: har video o'z mavzusi, o'z musiqasi va o'z klip to'plamiga ega bo'lsin; bir xil trek ko'p videoda ishlatilmasin;
  tavsifda aniq mavzu; AI yaratganligi haqida eslatma.
- Tibbiy va'dalar yo'q ("davolaydi", "uyqusizlikni yo'qotadi" deb yozilmaydi); faqat "relaxing", "calming", "background for sleep and study".
