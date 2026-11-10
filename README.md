# AutoExplainer (YotubeVideo)

Django app that turns a topic into a finished faceless explainer video (stick-figure style, English narration).
It is built in 10 phases; this README grows with each phase.

**Current state:** Uzbek bright UI; one **niche** ("Qadimgi odamlar va inson tabiati") that feeds every Gemini prompt;
studio (player, metadata, scene editor, own-image upload, AI images via Cloudflare); **Tomosha** (watch your videos and
reference-channel videos); **Kanallar** (YouTube Data API import, Gemini style analysis, topic ideas with dedup);
**Kutubxona** (music/SFX upload, auto-tags, preview, starter pack); **Qoidalar** (policy-page watcher on a
django-q2 schedule, change notes + banner, editable per-video compliance checklist).
Still to come: script generation (phase 2), voice (3), render (4/7), thumbnails (9).

## Setup (Windows, PowerShell)

```powershell
cd "D:\Django Projects\YotubeVideo"
python -m venv venv
.\venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
copy .env.example .env               # then edit .env (DJANGO_SECRET_KEY at minimum)
python manage.py migrate
python manage.py createsuperuser     # optional, for /admin
```

## Setup (Linux)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
```

## Run

`python manage.py dev` also applies pending migrations first.

One terminal (web server + background worker together, Ctrl+C stops both):

```
python manage.py dev                 # -> http://127.0.0.1:8000
```

Or, if you prefer, two separate terminals (both with the venv activated):

```
python manage.py runserver           # terminal 1 -> http://127.0.0.1:8000
python manage.py qcluster            # terminal 2 -> background worker (django-q2, ORM broker, no Redis)
```

## Verify Phase 1

1. `python manage.py test apps.videos` → all tests OK.
2. Open http://127.0.0.1:8000, create a project (e.g. "Why do cats purr?", 3 min).
3. On the project page click **Run demo job**: the progress bar moves
   Script ready → Approved → Generating assets → Rendering → Done in ~15 s without reloading the page.
   (If it stays on "Queued...", the `qcluster` terminal is not running.)
4. Go back to **New** and type "why cats purr" → a yellow "Similar video already made" warning appears;
   submitting requires ticking the confirm box.
5. **Projects** shows the project and the "finished in the last 7/30 days" counters.

## Pages

| Page | What it does |
|---|---|
| ✨ Yangi video | new project (defaults from the niche), duplicate-topic warning, topic suggestions |
| 📁 Videolar | permanent history, search/filter, 7/30-day cadence counters |
| ▶️ Tomosha | watch finished videos; watch reference-channel videos (embedded YouTube player) |
| 🎯 Nisha | the one niche: audience, tone, title formula, pillars, topics to avoid, originality rules, image style, main character |
| 📺 Kanallar | add a channel by URL/@handle -> import last 40 videos -> Gemini style notes -> 10 topic ideas |
| 🎵 Kutubxona | upload music/SFX (multi-file), auto-tags (Gemini or filename keywords), duration, preview, edit tags, delete, starter pack |
| 🛡️ Qoidalar | tracked YouTube policy pages, "check now", scheduled check every `POLICY_CHECK_INTERVAL_DAYS`, change notes, compliance checklist |

## Starter library (`starter_library/`)

Press **"Boshlang'ich to'plamni yuklash"** on the Kutubxona page (or it is skipped if already imported).
* 16 music tracks from **FreePD.com** (public domain / CC0), via the SoundSafari/CC0-1.0-Music dataset, re-encoded to 128 kbps.
* 11 UI sounds (ding / pop / click) from **Kenney** (CC0).
* 12 whoosh / swoosh / riser / boing / impact sounds **synthesized for this project** (CC0).
See `starter_library/licenses/`. Double-check licences yourself before monetizing.

## Images: Cloudflare Workers AI (free)

Scene images are drawn by the provider set in `.env` (`IMAGE_PROVIDER=cloudflare`, default).
Cloudflare gives 10,000 free "neurons" per day - roughly 150+ FLUX.1 [schnell] images/day.

1. Create a free account at https://dash.cloudflare.com (no card needed).
2. Account ID: dashboard -> **Workers AI** -> **Use REST API** (or the right sidebar of any page).
3. Token: **My Profile -> API Tokens -> Create Token -> template "Workers AI"** -> Create -> copy.
4. Put both into `.env`:
   ```
   CLOUDFLARE_ACCOUNT_ID=...
   CLOUDFLARE_API_TOKEN=...
   ```
5. Check: `python manage.py cf_test` -> writes `media/test_image.png`.

In the studio: **"Yetishmayotgan rasmlarni chizish"** draws every scene that has an image prompt but no image
(background job, one by one); each scene also has **"Rasm chizish / Qayta chizish"**. Hand-uploaded images are
never redrawn. FLUX returns a square picture; it is centre-cropped to 1920x1080, and every prompt asks the model
to keep the subject in the middle. If the daily quota runs out, the job stops and the remaining scenes are marked
with the reason - press the button again the next day.

## Speed & professional edit (render v2)

* **Parallel assets:** missing images (`IMAGE_CONCURRENCY`, default 3) and voice-overs (`TTS_CONCURRENCY`, default 4)
  are made at the same time. Voice-overs that fail get a second, one-by-one pass after a pause.
* **Parallel render:** scene clips are rendered by `RENDER_WORKERS` ffmpeg processes (0 = half the CPU threads).
  Unchanged clips are cached, so a re-render only redoes edited scenes (and the scene right after them).
* **Transitions:** each scene opens with an xfade out of the previous scene's last frame. Automatic rotation:
  dissolves, smooth pushes, zoom, circle and hard cuts; hook scenes stay hard cuts; punchlines get a white flash.
  The per-scene "Kirish o'tishi" choice overrides it. First scene fades up from black, last fades out.
* **Sound design:** quiet whoosh under movement transitions, impact under a punchline flash, plus the script's SFX cues.
  If the library is empty the CC0 starter pack is imported automatically at render time.
* **Audio mix:** narration gets a high-pass + compressor; music is ducked under the voice (sidechain) and the
  final mix is normalized to **-14 LUFS** (YouTube's target). Clip audio stays PCM, so AAC is encoded only once.
* **Motion & captions:** eased Ken Burns moves (slow start/stop); captions highlight the word being spoken
  (when the TTS gives word timings, e.g. Edge / ElevenLabs).

## Assumptions (so far)

- Django 5.2 LTS (supports Python 3.10–3.13). Python 3.11+ recommended.
- One django-q2 worker (`workers: 1`) to stay light on an i3 / 8 GB laptop; SQLite lock timeout raised to 30 s
  because the web server and worker share the DB file.
- Topic duplicate check = normalized token hash (lowercase, no punctuation/stopwords, light plural stemming,
  order-independent) plus a similarity score ≥ 0.6.
- Projects are only deleted by you from the UI; deleting also removes `media/projects/p<id>/`.
- Images default to Cloudflare Workers AI FLUX.1 [schnell] (free daily quota); Gemini images come in phase 5 as a paid option.
- UI is Uzbek (`LANGUAGE_CODE = "uz"`); the videos themselves are English.
- No CSS framework: one small stylesheet `static/css/app.css` (light + dark). HTMX is bundled in `static/js/`, so the UI works offline.
- Hand-uploaded scene images are normalized to 1920x1080 and marked `image_locked` (never regenerated by AI).
- Editing narration drops that scene's cached voice-over; editing the image prompt drops an AI image; any edit marks the project "needs re-render".
