"""Builds scripts/ai_nima.json and scripts/ai_nima.factcheck.md (TeachAI, Uzbek).
(run: ./venv/Scripts/python scripts/ai_nima.py)
Tuple: (narration, image_prompt, beat, emotion, intensity, pace, pause_ms, sfx, kind, fact_source). kind: "fact" (has a source) | "explain"."""
import json
from pathlib import Path

OECD = "OECD (2023). Recommendation of the Council on Artificial Intelligence: updated definition of an AI system, adopted 8 November 2023; explanatory memorandum on the updated OECD definition of an AI system (2024)"
LEC = "LeCun, Bengio & Hinton (2015). Deep learning. Nature 521, 436-444"
BRO = "Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS 2020 (arXiv:2005.14165)"
JI = "Ji et al. (2023). Survey of Hallucination in Natural Language Generation. ACM Computing Surveys 55(12), 248"
OUY = "Ouyang et al. (2022). Training language models to follow instructions with human feedback. NeurIPS 2022 (arXiv:2203.02155)"
VAS = "Vaswani et al. (2017). Attention Is All You Need. NeurIPS 2017"
KRI = "Krizhevsky, Sutskever & Hinton (2012). ImageNet classification with deep convolutional neural networks. NeurIPS 2012"
EPO = "Epoch AI (2025). The training compute of notable AI models is doubling roughly every five months. epoch.ai data insights"
IEA = "International Energy Agency (2025). Energy and AI (executive summary)"
TUR = "Turing, A. M. (1950). Computing Machinery and Intelligence. Mind 59(236), 433-460"
MCC = "McCarthy, Minsky, Rochester & Shannon (1955). A proposal for the Dartmouth summer research project on artificial intelligence (1956 workshop); OED use cited by Language Log"
LIG = "Lighthill report to the British Science Research Council (1973), as described in AI-history summaries (DataCamp, Medium); the second downturn late 1980s"
CAM = "Campbell, Hoane & Hsu (2002). Deep Blue. Artificial Intelligence 134, 57-83; IEEE Spectrum, Chip Hall of Fame: IBM Deep Blue 2 chess chip (match May 1997)"
ALP = "AlphaGo versus Lee Sedol, Seoul, 9-15 March 2016 (TechCrunch, 9 March 2016)"
UBS = "UBS analyst note reported by Reuters, 1-2 February 2023: ChatGPT estimated at 100 million monthly active users in January 2023 (Similarweb data); OpenAI release 30 November 2022"
AIX = "Stanford HAI (2025). Artificial Intelligence Index Report 2025"
UZB = "Strategy for the development of artificial intelligence technologies until 2030, approved by the President of Uzbekistan on 14 October 2024 (No. PQ-358; gov.uz, lex.uz)"

VERIFY = {
    OECD: ("Searched 2026-10-24: OECD Council adopted the revised definition on 8 November 2023 (summary pages). The official text could not be opened (403), so the wording is a paraphrase of secondary summaries.", "Paraphrase only, no quotation marks; level 2 (secondary summary of a primary source)."),
    LEC: ("Searched 2026-10-24: Nature 521(7553), 436-444; abstract opens with models composed of multiple processing layers learning representations with multiple levels of abstraction. Full text not opened.", "Abstract-level only; level 1 (peer-reviewed)."),
    BRO: ("Searched 2026-10-24: arXiv abstract: GPT-3 is an autoregressive language model with 175 billion parameters. The 300-billion-token figure was NOT confirmed and is not used.", "Only the parameter count and 'autoregressive' (predicts the next piece of text); level 1."),
    JI: ("Searched 2026-10-24: ACM Computing Surveys 55(12) 2023; abstract says deep-learning-based generation is prone to hallucinate unintended text. The formal definition wording was not opened.", "Stated as a well-studied problem, no numbers; level 1."),
    OUY: ("Searched 2026-10-24: labelers wrote demonstrations and ranked model outputs, used for supervised fine-tuning and RLHF; 1.3B InstructGPT outputs preferred to 175B GPT-3.", "Only the human demonstrations and rankings are used; level 1."),
    VAS: ("Searched 2026-10-24: abstract: a new architecture based solely on attention mechanisms, dispensing with recurrence and convolutions; NeurIPS 2017. 'Many current large language models use it' is general knowledge (GPT stands for Generative Pre-trained Transformer) and is worded loosely.", "'Ko'pgina' (many), not 'all'; level 1."),
    KRI: ("Searched 2026-10-24: abstract: winning top-5 test error 15.3 percent vs 26.2 percent for the second-best entry in ILSVRC-2012; GPU implementation credited. 'Two GPUs' comes from secondary summaries (GTX 580 pair) and is worded softly.", "Numbers exact from the abstract; level 1 plus secondary for the two GPUs."),
    EPO: ("Searched 2026-10-24: Epoch AI pages: doubling roughly every five to six months since 2010 (4.4x to 4.7x per year depending on the page version). Epoch's own data page not opened directly.", "'Taxminan har besh-olti oyda' (roughly every five to six months); level 2 (research institute data)."),
    IEA: ("Searched 2026-10-24: IEA Energy and AI: data centres used about 415 TWh in 2024, about 1.5 percent of global electricity; projected to more than double to about 945 TWh by 2030. The 2030 share is not stated by IEA.", "Called a projection; no 2030 share quoted; level 1 (intergovernmental agency)."),
    TUR: ("Searched 2026-10-24: Mind 59(236), October 1950, pp. 433-460; opens with 'I propose to consider the question, Can machines think?'.", "Level 1."),
    MCC: ("Searched 2026-10-24: Language Log citing the OED: first use of the term in the 1955 grant application by McCarthy, Minsky, Rochester and Shannon proposing a 2-month study at Dartmouth in 1956. Popular accounts say McCarthy coined it at the 1956 workshop; careful accounts place it in the 1955 proposal.", "Worded 'first written in the 1955 proposal'; level 2."),
    LIG: ("Searched 2026-10-24: only secondary sources (DataCamp, Medium) describe the 1973 Lighthill report cutting UK funding and a second downturn in the late 1980s; no academic history opened.", "Hedged: 'according to some historical accounts'; level 3, flagged weak."),
    CAM: ("Searched 2026-10-24: Deep Blue beat Kasparov in May 1997 (3.5-2.5 rematch); the Campbell, Hoane and Hsu paper lists a single-chip chess search engine, a massively parallel system and a complex evaluation function. Numbers of positions per second were NOT confirmed and are not used.", "No numbers; level 1 plus IEEE Spectrum."),
    ALP: ("Searched 2026-10-24: AlphaGo beat Lee Sedol 4-1 in Seoul, 9-15 March 2016.", "Level 2."),
    UBS: ("Searched 2026-10-24: Reuters report of the UBS note: estimated 100 million monthly active users in January 2023, about two months after launch; based on Similarweb data; announced 30 November 2022.", "Called an analyst estimate, not an OpenAI figure; level 2."),
    AIX: ("Searched 2026-10-24 (summaries of the AI Index 2025): 78 percent of organizations reported using AI in 2024 vs 55 percent in 2023; GPT-3.5-level cost fell from 20 dollars to 0.07 dollars per million tokens (Nov 2022 to Oct 2024); private AI investment 252.3 billion dollars in 2024. The report itself was not opened.", "Attributed to the Stanford report; level 2 via summaries."),
    UZB: ("Searched 2026-10-24: gov.uz announcement and lex.uz: strategy approved 14 October 2024; priority areas regulation, infrastructure and skills; sources label the act PQ-358 or RP-358.", "'Tasdiqlangan' without the document number; level 1 (official)."),
}

S = [
    # ---------------- hook
    ("Siz bugun sun'iy intellektdan, ehtimol, allaqachon foydalandingiz.", "A young man walks through a modern city street in morning light, looking at his smartphone and smiling", "hook", "curious", 2, "normal", 0, "impact", "explain", None),
    ("Qidiruv, tarjima, kamera: ularning ko'pi shunga tayanadi.", "Close-up of a hand holding a smartphone taking a photo of a historic building, soft daylight", "hook", "curious", 2, "normal", 0, None, "explain", None),
    ("Lekin u aslida qanday ishlaydi, bilasizmi?", "A thoughtful woman at a desk looking at a laptop with a puzzled expression, window light", "hook", "tense", 2, "normal", 0, None, "explain", None),
    ("Bu videoda uni boshidan, oddiy tilda tushuntiraman.", "A friendly teacher at a whiteboard smiling at a small class, bright classroom", "hook", "serious", 2, "normal", 0, None, "explain", None),
    ("Oxirida sun'iy intellekt nima ekanini aniq tushunasiz.", "Students nodding and taking notes in a bright university lecture hall", "hook", "curious", 3, "normal", 0, None, "explain", None),
    ("Nimaga tayanishini va qanday paydo bo'lganini bilasiz.", "Old computer equipment in a technology museum next to a modern laptop, warm light", "hook", "curious", 2, "normal", 0, None, "explain", None),
    ("Nega u hayotimizga bunchalik tez kirganini ham.", "A busy city crossing at dusk with glowing shop windows and people using phones", "hook", "excited", 2, "normal", 0, "pop", "explain", None),
    ("Chunki bu bilim endi har kimga kerak bo'ladi.", "A group of adults of different ages working together at a laptop in a bright office", "hook", "serious", 3, "normal", 0, None, "explain", None),
    ("Foydali bo'lsa, obuna bo'ling, birga o'rganamiz.", "A smiling woman in a cozy home study looking toward the camera, soft light", "hook", "happy", 2, "normal", 0, None, "explain", None),
    ("Oxirida bitta muhim ehtiyot choramni ham aytaman.", "A hand holding a magnifying glass over a printed page on a wooden table", "hook", "whisper", 2, "slow", 0, None, "explain", None),
    ("Boshlaymiz. Avval eng oddiy savoldan.", "Sunrise over a calm modern city skyline, golden light", "hook", "curious", 2, "normal", 0, None, "explain", None),
    ("Sun'iy intellekt aslida nima?", "A curious child looking at a glowing laptop screen in a dim room, face lit softly", "hook", "curious", 2, "slow", 300, None, "explain", None),
    # ---------------- 1. what is AI
    ("Sun'iy intellekt: odam aqli talab qiladigan ishlarni bajara oladigan kompyuter tizimi. Tushunish, tarjima qilish, rasm tanish, qaror taklif qilish.", "A teacher explaining at a whiteboard to attentive students, bright classroom, natural light", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Iqtisodiy hamkorlik va taraqqiyot tashkiloti buni shunday izohlaydi: tizim olgan ma'lumotdan o'zi xulosa chiqaradi va bashorat, matn, tavsiya yoki qaror yaratadi.", "Printed policy documents and a pen on a desk beside a laptop in a quiet office", "build", "neutral", 2, "normal", 0, None, "fact", OECD),
    ("Ikki dasturni solishtiramiz. Oddiy dastur faqat sizning yozgan qoidangizni bajaradi. Sun'iy intellekt esa qoidani o'zi topadi.", "A calculator and a laptop side by side on a wooden desk, soft light", "build", "curious", 2, "normal", 0, None, "explain", None),
    ("Tasavvur qiling, bolaga mushuk nima ekanini o'rgatyapsiz. Qoida aytmaysiz, shunchaki ko'p mushuk ko'rsatasiz.", "A mother showing a picture book with a cat to a small child on a sofa, warm light", "build", "happy", 2, "normal", 0, None, "explain", None),
    ("Bola o'zi sezadi: quloq, mo'ylov, dum. Sun'iy intellekt ham misollardan shunday o'rganadi. Menimcha, bu eng oddiy va eng to'g'ri tushuntirish.", "A child pointing at a real cat sitting on a sofa, laughing, warm home light", "build", "happy", 2, "normal", 0, None, "explain", None),
    ("Bunga mashinali o'qitish deyiladi: dastur qoidani o'zi emas, ma'lumotdan topadi.", "Many printed photographs of cats and dogs spread on a table, top-down view", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Eng kuchli turi chuqur o'rganish. U ko'p qatlamli modellar yordamida ma'lumotdan bosqichma-bosqich murakkabroq belgilarni o'rganadi.", "Several layers of glass panes stacked in a row with light passing through them, studio photo", "build", "neutral", 2, "normal", 0, None, "fact", LEC),
    ("Buni bir necha elakdan o'tkazishga o'xshatish mumkin: birinchi qatlam chiziqlarni, keyingisi shaklni, oxirgisi mushukni topadi.", "A stack of kitchen sieves above each other with flour falling through, close-up", "build", "curious", 2, "normal", 0, None, "explain", None),
    # ---------------- 2. how it works
    ("Ishlash ikki bosqichdan iborat: avval o'qitish, keyin foydalanish.", "A student studying with open books at a library desk, side window light", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("O'qitishda model misolni ko'radi, javob beradi, xato qiladi va xatosidan sozlanadi. Bu millionlab marta takrorlanadi.", "A student correcting mistakes in a notebook with a red pen, close-up", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Masalan, Ji Pi Ti uch modeli bir yuz yetmish besh milliard parametrga ega edi. Parametr: modelning ichidagi sozlanadigan raqam.", "Close-up of a large audio mixing console with hundreds of knobs and sliders, studio light", "build", "curious", 2, "normal", 0, None, "fact", BRO),
    ("Chat Ji Pi Ti kabi til modellari bitta oddiy ish qiladi: matnning keyingi bo'lagini taxmin qiladi, so'ng yana keyingisini.", "Hands typing on a smartphone keyboard, blurred screen, shallow depth of field", "build", "neutral", 2, "normal", 0, None, "fact", BRO),
    ("Shuning uchun u ba'zan ishonch bilan noto'g'ri gapiradi. Tadqiqotchilar buni gallyutsinatsiya deb ataydi va uni ancha o'rganishgan.", "A person comparing a laptop screen with an open reference book, skeptical look", "build", "serious", 2, "normal", 0, None, "fact", JI),
    ("Demak, muhim ma'lumotni har doim ikkinchi manbadan tekshiring.", "A woman checking a fact in an encyclopedia while reading on a laptop", "punchline", "serious", 3, "normal", 400, None, "explain", None),
    # ---------------- 3. what it needs
    ("Endi asosiy savol: bularning ishlashi uchun aynan nimalar kerak? Beshta narsa.", "A long modern data center corridor with rows of server racks, cool blue light", "build", "curious", 2, "normal", 0, None, "explain", None),
    ("Birinchisi: ma'lumot. Model qancha ko'p va sifatli misol ko'rsa, shuncha yaxshi o'rganadi.", "A vast library with tall shelves of books, warm light", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Ikkinchisi: hisoblash quvvati. Ikki ming o'n ikkinchi yilda mashhur Aleksnet modeli grafik protsessorlarda, taxminan ikkitasida, o'qitilgan.", "Close-up of a graphics card with fans inside a computer case, studio light", "build", "neutral", 2, "normal", 0, None, "fact", KRI),
    ("Epok Ey Ay tadqiqot markazi hisobiga ko'ra, taniqli modellarni o'qitishga ketadigan hisoblash hajmi 2010-yildan beri taxminan har besh-olti oyda ikki baravar oshgan.", "A wide shot of a modern research data lab with glowing monitors, cool light", "build", "awe", 2, "normal", 300, "riser", "fact", EPO),
    ("Uchinchisi: algoritm, ya'ni o'rganish usuli. Yaxshi g'oya bir xil quvvatda ancha yaxshi natija beradi.", "A researcher sketching a diagram on a notepad at a desk, warm lamp light", "build", "curious", 2, "normal", 0, None, "explain", None),
    ("To'rtinchisi: energiya. Xalqaro Energetika Agentligi hisobiga ko'ra, 2024-yilda ma'lumotlar markazlari dunyo elektrining taxminan bir yarim foizini sarflagan.", "Exterior of a large modern data center building with power lines at dusk", "build", "curious", 2, "normal", 0, None, "fact", IEA),
    ("Agentlik bu ko'rsatkich 2030-yilga kelib ikki baravardan ko'proq oshishi mumkinligini taxmin qiladi. Bu bashorat, aniq natija emas.", "High-voltage transmission towers at sunset, wide shot", "build", "serious", 2, "normal", 0, None, "fact", IEA),
    ("Beshinchisi: odamlar. Masalan, Openey Ay Ay tadqiqotchilarida odamlar namuna javob yozgan va modelning javoblarini baholab chiqqan.", "Two analysts reviewing printed answers and marking them with pens at a table", "build", "neutral", 2, "normal", 0, None, "fact", OUY),
    ("Demak, sun'iy intellekt sehr emas: bu ma'lumot, quvvat va insonlar mehnati evaziga qurilgan mashina. Menga shu fikr eng muhimdek tuyuladi: uni sehr emas, vosita deb biling.", "Engineers working together at computers in a bright office, candid photo", "punchline", "serious", 2, "slow", 400, None, "explain", None),
    # ---------------- subscribe (mid-video)
    ("Qisqa tanaffus. Agar tushunarli bo'layotgan bo'lsa, obuna bo'ling va biz bilan qoling. Sun'iy intellektni oddiy tilda birga o'rganishda davom etamiz. Bu bepul, bir soniya oladi va boshqalarga ham kanalni topishga yordam beradi.", "A smiling woman in a cozy home study waving toward the camera, soft warm light", "normal", "happy", 2, "normal", 300, None, "explain", None),
    # ---------------- 4. how it began
    ("Endi ikkinchi savol: bularning hammasi qanday paydo bo'lgan? Hikoya yetmish yildan ortiq davom etadi.", "An old mainframe computer cabinet in a technology museum with soft light", "build", "curious", 2, "normal", 0, None, "explain", None),
    ("Ming to'qqiz yuz ellikinchi yilda Alan Tyuring o'zining mashhur maqolasini shunday savol bilan boshladi: mashinalar fikrlay oladimi?", "A vintage typewriter and an old printed journal on a wooden desk, warm light", "build", "neutral", 2, "normal", 0, None, "fact", TUR),
    ("'Sun'iy intellekt' atamasi yozma holda birinchi marta 1955-yildagi taklifda uchraydi. Unga ko'ra, 1956-yilda Dartmut kollejida ikki oylik tadqiqot yozi o'tishi kerak edi.", "An old stone college building in autumn light with a green lawn, classic architecture", "build", "curious", 2, "normal", 0, None, "fact", MCC),
    ("Ba'zi tarixiy bayonlarga ko'ra, 1973-yildagi Laythil hisoboti Buyuk Britaniyada mablag'ni keskin qisqartirgan. Bunday sovuq davrlarni sun'iy intellekt qishi deyishadi.", "A frosty window of an old university building at winter dusk", "build", "serious", 2, "normal", 0, None, "fact", LIG),
    ("Ming to'qqiz yuz to'qson yettinchi yil mayida Ay Bi Em kompyuteri Dip Blu shaxmatda jahon chempioni Garri Kasparovni mag'lub etdi.", "A chessboard with pieces in a mid-game position and a chess clock on a table, dramatic side light", "build", "awe", 2, "normal", 300, None, "fact", CAM),
    ("Lekin Dip Blu o'rganmagan edi: u maxsus chip bilan juda ko'p variantni qidirgan va odamlar yozgan baholash qoidalariga tayangan.", "A macro photo of a custom computer chip on a circuit board", "build", "neutral", 2, "normal", 0, None, "fact", CAM),
    ("Ikki ming o'n ikkinchi yilda Aleksnet rasm tanish musobaqasida xatoni o'n besh butun o'ndan uch foizga tushirdi. Ikkinchi natija yigirma olti butun o'ndan ikki foiz edi.", "Hundreds of colorful printed photographs of animals, objects and places spread on a floor, top-down view", "build", "awe", 3, "normal", 300, "ding", "fact", KRI),
    ("Ikki ming o'n oltinchi yil martida Alfago go o'yinida Li Sedolni to'rt-bir hisobida yutdi.", "A go board with black and white stones in a quiet room, close-up", "build", "neutral", 2, "normal", 0, None, "fact", ALP),
    ("Ikki ming o'n yettinchi yilda Gugl tadqiqotchilari Transformer g'oyasini e'lon qilishdi. U faqat diqqat mexanizmiga tayanadi. Hozirgi ko'pgina katta til modellari shu g'oyadan foydalanadi.", "A researcher presenting a concept to colleagues on a large screen in a conference room, side view", "build", "curious", 2, "normal", 0, None, "fact", VAS),
    ("Ikki ming yigirma ikkinchi yil o'ttiz noyabrda Chat Ji Pi Ti hammaga ochildi. Yu Bi Es baholashicha, ikki oyda u yuz million oylik faol foydalanuvchiga yetgan.", "A crowd of diverse people looking at their smartphones in a city square at dusk", "build", "awe", 2, "normal", 400, "riser", "fact", UBS),
    # ---------------- 5. why so fast
    ("Endi uchinchi savol: nega u shunchalik tez hayotimizning bir qismiga aylanyapti? Beshta sabab bor.", "A busy modern city street at rush hour with people using phones, motion blur", "build", "curious", 2, "normal", 0, None, "explain", None),
    ("Birinchisi: oddiy muloqot. Siz o'z tilingizda yozasiz yoki gapirasiz, tizim tushunadi. Albatta, o'zbek tilida sifat hali har xil bo'lishi mumkin.", "A grandmother speaking into a smartphone in a cozy living room, curious smile", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Ikkinchisi: u allaqachon cho'ntagingizda. Telefon, brauzer va ofis dasturlari ichida.", "A close-up of a smartphone in a jacket pocket on a street, shallow depth of field", "build", "happy", 2, "normal", 0, None, "explain", None),
    ("Stenford universitetining 2025-yilgi hisobotiga ko'ra, 2024-yilda tashkilotlarning yetmish sakkiz foizi sun'iy intellektdan foydalanganini aytgan. Bir yil avval bu ellik besh foiz edi.", "A modern open office with colleagues using laptops, bright daylight", "build", "curious", 2, "normal", 0, None, "fact", AIX),
    ("Uchinchisi: u arzonlashdi. Narx tushsa, texnologiya hammaga yetib boradi.", "A small shop owner using a tablet at a market stall, natural light", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Xuddi shu hisobotga ko'ra, Ji Pi Ti uch va yarim darajasidagi javob narxi 2022-yil noyabridan 2024-yil oktyabrigacha million belgi uchun yigirma dollardan yetmish sentgacha tushgan.", "A row of coin stacks shrinking in height from tall to short on a wooden table, studio photo", "build", "awe", 2, "normal", 300, None, "fact", AIX),
    ("To'rtinchisi: bitta tizim ko'p ishga yaraydi: yozish, tarjima, rasm, kod, tahlil. Shuning uchun har kasb egasi undan foydalana oladi.", "A teacher, a farmer and a shop owner standing together outdoors, each holding a tablet, daylight", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Beshinchisi: pul va raqobat. 2024-yilda xususiy sun'iy intellekt sarmoyasi ikki yuz ellik ikki butun o'ndan uch milliard dollarga yetgan.", "Tall glass skyscrapers of a financial district at golden hour", "build", "neutral", 2, "normal", 0, None, "fact", AIX),
    ("O'zbekistonda ham 2024-yil o'n to'rtinchi oktyabrda 2030-yilgacha sun'iy intellektni rivojlantirish strategiyasi tasdiqlangan. U qoidalar, texnik infratuzilma va ko'nikmalarni o'z ichiga oladi.", "A modern government building with national flags under a clear blue sky", "build", "neutral", 2, "normal", 0, None, "fact", UZB),
    ("Menimcha, bu moda emas. Elektr yoki internet singari, sekin-asta ko'rinmas, lekin zarur qatlamga aylanadi.", "A light switch on a wall in warm evening light next to a window, shallow depth of field", "build", "serious", 2, "slow", 0, None, "explain", None),
    # ---------------- 6. practical + recap
    ("Endi amaliy qism. Birinchi qadam: oddiy savol bering va javobini ikkinchi manbadan tekshiring.", "A student asking a question on a laptop with an open book beside it to double-check, desk light", "build", "neutral", 2, "normal", 0, None, "explain", None),
    ("Ikkinchi qadam: parol, pasport raqami va karta ma'lumotlarini chatga hech qachon kiritmang.", "A closed padlock resting on a laptop keyboard, macro photo", "build", "serious", 2, "normal", 0, None, "explain", None),
    ("Uchinchisi: sog'liq, huquq yoki pul haqidagi qarorlarda mutaxassisga tayaning. Sun'iy intellekt yordamchi bo'lishi mumkin, hakam emas.", "A professional adviser and a client talking calmly across a desk in a bright office", "build", "serious", 2, "normal", 0, None, "explain", None),
    ("Bugun uchta narsani bilib oldik: u ma'lumotdan o'rganadi; ma'lumot, quvvat, energiya va odamlarga tayanadi; va arzon, oddiy bo'lgani uchun tez tarqalmoqda.", "A teacher at a whiteboard holding up three fingers in a bright classroom, smiling", "build", "happy", 2, "normal", 0, None, "explain", None),
    ("Vaqt ajratganingiz uchun rahmat. Foydali bo'lsa, layk bosing va qaysi mavzuni tushuntirishimni izohda yozing: men har birini o'qiyman. Keyingi videoda Chat Ji Pi Ti nega xato qilishini yanada chuqurroq ko'ramiz. Ko'rishguncha, do'stim.", "A smiling woman in a cozy home study waving goodbye in warm evening light", "normal", "happy", 2, "slow", 800, "pop", "explain", None),
]

assert 56 <= len(S) <= 86, len(S)
scenes = []
for i, (narr, prompt, beat, emo, inten, pace, pause, sfx, kind, src) in enumerate(S):
    assert (beat == "hook") == (i < 12), i + 1
    assert (kind == "fact") == bool(src), (i + 1, kind)
    assert "—" not in narr and "–" not in narr, i + 1
    scenes.append({"narration": narr, "image_prompt": prompt, "beat_type": beat, "sfx_cue": sfx, "scene_kind": kind,
                   "fact_source": src, "emotion": emo, "intensity": inten, "pace": pace, "pause_after_ms": pause})

data = {
    "title": "Sun'iy intellekt nima va u qanday ISHLAYDI?",
    "title_alternatives": ["Sun'iy intellekt nega hayotimizga shunchalik TEZ kirdi?", "Sun'iy intellekt qanday O'RGANADI? Oddiy tilda",
                           "Sun'iy intellektning 70 yillik TARIXI", "Sun'iy intellektni 9 daqiqada TUSHUNING"],
    "description": ("Siz bugun sun'iy intellektdan, ehtimol, allaqachon foydalandingiz. Bu videoda sun'iy intellekt nima ekanini, qanday ishlashini, ishlashi uchun nimalar kerakligini, "
                    "qanday paydo bo'lganini va nega hayotimizga shunchalik tez kirib kelayotganini oddiy tilda tushuntiramiz.\n\n"
                    "Bu video ta'lim maqsadida; tibbiy, huquqiy yoki moliyaviy maslahat emas.\n\nManbalar:\n"
                    "- LeCun, Bengio & Hinton (2015). Deep learning. Nature.\n- Brown et al. (2020). Language Models are Few-Shot Learners. NeurIPS.\n"
                    "- Vaswani et al. (2017). Attention Is All You Need. NeurIPS.\n- Krizhevsky, Sutskever & Hinton (2012). ImageNet classification with deep convolutional neural networks.\n"
                    "- Epoch AI (2025). Training compute of notable AI models.\n- IEA (2025). Energy and AI.\n- Stanford HAI (2025). AI Index Report 2025."),
    "tags": ["sun'iy intellekt", "AI", "ChatGPT", "o'zbek tilida", "mashinali o'qitish", "neyron tarmoq", "texnologiya", "TeachAI", "artificial intelligence", "how AI works"],
    "mood": "calm",
    "sources": [x for x in dict.fromkeys(s[9] for s in S if s[9])][:16],
    "scenes": scenes,
}
out = Path(__file__).with_suffix(".json")
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

md = ["# Fact-check: Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI)", "",
      "Har faktli sahna, manba, manba darajasi, qanday tekshirilgani va so'z ehtiyotkorligi. Tekshirilgan sana: 2026-10-24.", "",
      "## Usul", "- Har faktli sahnada manba bor; manba darajalari: 1 = hakamlik qilingan ish yoki rasmiy hujjat, 2 = ishonchli ikkilamchi manba, 3 = zaif/ikkilamchi (belgilangan).",
      "- Faqat annotatsiya yoki qidiruv xulosasi ko'rilgan joylarda shunday deb yozilgan; to'liq matn ochilmagan.",
      "- Tasdiqlanmagan raqamlar (GPT-3 ning 300 milliard tokeni, Deep Blue ning sekundiga pozitsiyalari) videoga kiritilmagan.",
      "- Matnda tibbiy, huquqiy yoki moliyaviy maslahat yo'q; oxirida mutaxassisga murojaat qilish aytiladi.", "",
      "## Faktli sahnalar", "", "| # | Sahna (qisqartirilgan) | Manba | Qanday tekshirilgan | So'z ehtiyotkorligi / daraja |", "|---|---|---|---|---|"]
for i, sc in enumerate(scenes, start=1):
    if sc["scene_kind"] == "fact":
        how, safe = VERIFY.get(sc["fact_source"], ("", ""))
        md.append(f"| {i} | {sc['narration'][:80].replace('|', '/')}... | {sc['fact_source'][:110].replace('|', '/')} | {how} | {safe} |")
md += ["", "## Tashlangan yoki yumshatilgan da'volar",
       "- GPT-3 o'qitish ma'lumotining 300 milliard token ekani: tasdiqlanmadi, tashlandi.",
       "- Deep Blue ning sekundiga qancha pozitsiya ko'rishi: tasdiqlanmadi, tashlandi.",
       "- 'Sun'iy intellekt' atamasini McCarthy 1956-yilda o'ylab topgan: ehtiyotkor manbalar uni 1955-yildagi taklifda ko'rsatadi, shuning uchun shunday yozilgan.",
       "- Sun'iy intellekt qishlari: faqat ikkilamchi manbalar; 'ba'zi tarixiy bayonlarga ko'ra' deb yumshatilgan.",
       "- Ma'lumot markazlarining 2030-yildagi ulushi: IEA aytmagan, kiritilmadi; faqat 'ikki baravardan ko'proq' (bashorat).",
       "- Iqtisodiy hamkorlik va taraqqiyot tashkilotining ta'rifi: rasmiy matn ochilmadi (403), parafraz sifatida berilgan.",
       "- Stenford hisoboti: faqat xulosa sahifalari ko'rildi, hisobotning o'zi emas.",
       "", "## Ustozlik va inson ovozi (bajarilgan)",
       "- Har tushuncha: savol, o'xshatish (mushuk va bola, elak, pult, telefon klaviaturasi, marker), ta'rif, misol; xato tasavvur tuzatildi (gallyutsinatsiya).",
       "- Shaxsiy fikrlar: 'Menimcha...' (ikki joyda). Hook: nima haqida, nimani olasiz, nega hozir, obuna, ochiq savol (ehtiyot chorasi oxirida).",
       "- Raqamlar so'z bilan; chet so'zlar o'zbekcha o'qilishi bilan yozilgan (Chat Ji Pi Ti, Aleksnet, Alfago, Dip Blu, Ay Bi Em)."]
Path(__file__).with_name("ai_nima.factcheck.md").write_text("\n".join(md), encoding="utf-8")

wpm = 112
words = sum(len(s["narration"].split()) for s in scenes)
print(out, len(scenes), "scenes,", words, "words, ~", round(words / wpm, 1), "min; hook words:", sum(len(s["narration"].split()) for s in scenes[:12]),
      "max hook line:", max(len(s["narration"].split()) for s in scenes[:12]))
em = [s["emotion"] for s in scenes]
run = 1
for i in range(1, len(em)):
    run = run + 1 if em[i] == em[i - 1] else 1
    if run > 3:
        print("4+ same emotion in a row at scene", i + 1, em[i])
print("subscribe scenes:", [i + 1 for i, s in enumerate(scenes) if "obuna" in s["narration"].lower()], "of", len(scenes))
