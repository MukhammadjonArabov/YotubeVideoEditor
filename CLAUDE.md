# AutoExplainer (YotubeVideo)

Django app that turns a script into a finished faceless explainer video (hand-drawn stick-figure style,
English narration) for a monetized YouTube channel. Niche: ancient humans and the science of everyday
human life. The owner writes to you in **Uzbek**: always answer in Uzbek. Videos and scripts are English.

## Commands (Windows, run from the repo root)

- Python: `./venv/Scripts/python` (Bash) or `.\venv\Scripts\python` (PowerShell)
- Tests: `./venv/Scripts/python manage.py test apps.videos`
- App + worker: `python manage.py dev` -> http://127.0.0.1:8000
- DB is PostgreSQL (`DATABASE_URL` in `.env`). Never print `.env` secrets.
- Windows Smart App Control blocks some unsigned DLLs (psycopg-binary, PyAV). Workarounds already exist:
  `config/settings.py` `_use_system_libpq`, `services/align.py` stubs PyAV. Test any new native library first.
- Printing Uzbek text with emoji from Python in Bash: prefix `PYTHONIOENCODING=utf-8`.

## Who does what (save Claude tokens)

- **Gemini (the app's `GEMINI_API_KEY`) does the analysis**: reference-channel research, topic suggestions
  (Kanallar page), director marks, compliance check, image QA. Do not redo channel or competitor analysis by
  hand; read what `video_check` prints (it uses the channel data Gemini already collected).
- **Claude (you) writes**: the Uzbek concept, the English script with per-scene voice acting, and all prompts
  (image prompts, hook video prompts). WebSearch/WebFetch only to verify facts.
- **Generation of pictures / hook clips** is not done by you: the Chrome extension in `flow_extension/` works
  through the Flow queue (see "Hook video" below). Never drive Flow by hand through the browser tools.

## Second niche: TeachAI (Uzbek, AI and new technology)

Since 2026-10-24 the owner also runs **TeachAI**: Uzbek-language educational videos about AI and new technologies, photorealistic scene pictures (NOT stickman),
a patient teacher's tone, a hook that says what the video is, what the viewer gets and asks for a subscribe. Everything about it is in
`niches/TeachAI.md` (read it before touching a TeachAI idea). The owner gives the idea; you research, write the Uzbek script, and produce the video.
## Third niche: Musiqa (relaxing music, since 2026-10-25)

Spec: `niches/Musiqa.md`. One 3-4 min ElevenLabs track (wordless female vocalise + nature) looped to 20-30 min over looped
Google Flow clips. Claude writes a spec JSON (`scripts/music/<slug>.json`: music prompt, 2-6 Flow prompts, 3 titles, description,
tags, 3 thumbnail Flow prompts) and runs `manage.py music_new <spec> [--project N]`; the owner listens to takes, edits prompts,
uploads clips and starts the montage at `/musiqa/<id>/`. Every take is auto-checked (`services/music_qc.py`, `manage.py music_qc`).
ElevenLabs Music API needs a paid plan (free plan returns 402); uploading a ready track works without it.

The rest of this file describes the original ancient-humans niche (English, stickman). Some code is still niche-specific: see section 11 of that file.

## The video workflow: idea -> concept -> approval -> script

The owner writes a short idea in Uzbek plus the length in minutes. Scripts are written by you (Claude)
inside Claude Code; there is no Anthropic API key in this project.

### The site is read-only (since 2026-10-23)

The owner runs everything through Claude. The site (`/`) only shows statistics, videos in progress, finished videos
and, per video, the **publish kit**: 3 title options, 1 description (with chapters and sources), tags and 3 thumbnails.
The old pages (script import, approval, scene editor, Flow, music videos, channels, library, rules) were moved to
`_archive/2026-10-23-ui-cleanup/`; the models, tasks and services behind them are untouched.

After every finished video, ALWAYS create its kit (without being asked). Since 2026-10-24 the owner makes the preview pictures
himself in Google Flow, so DO NOT draw previews (no `--specs`, no `previews.json`); give him 3 Flow prompts instead:
1. Write `scripts/kits/p<id>.description.txt` (hook line, 2-line summary, "Chapters:" with real timestamps computed from
   the scene audio durations scaled to `actual_duration_sec`, "Sources:", the disclaimer, 3 hashtags).
2. Look at a contact sheet of the video's images to pick strong ideas (hero scene with a clear face, a fact scene with a strong object).
3. Write `scripts/kits/p<id>.flow.json`: 3 objects `{"text": "<2-4 words>", "prompt": "<Google Flow image prompt in the channel
   style: the SAME stick-figure man described in full, the scene, and the title text drawn inside the picture in huge yellow/white
   block capitals with a black outline, spelled exactly>"}` (see `scripts/make_flow_old.py` for the prompt pattern). Then
   `./venv/Scripts/python manage.py video_kit <id> --titles "A" "B" "C" --description-file ... --tags "..." --flow-prompts scripts/kits/p<id>.flow.json`
   (titles under 60 characters, one CAPS word each; tags under 500 characters).
4. Tell the owner (Uzbek) the titles and the page link. If a video's chapters change after a re-render, recompute them.
Old drawn thumbnails (`services/kit.py`, Pillow) still exist for earlier videos; every earlier video now also has its 3 Flow prompts.

### Autonomous mode ("mavzu top")

If the owner asks you to find the topic yourself, do NOT wait for concept or script approval and do not ask
permission between steps: pick a new topic that `video_check` shows is unmade and competitive, run steps 1-3,
fix compliance warnings, approve the project (`set_status(APPROVED)`), then enqueue `produce_video` (images +
voice + render; NO burned-in subtitles, `captions=False`, owner's rule 2026-11-10, because each video also ships Spanish and French audio) and report in Uzbek when it is finished. Never spend money without
asking; free quotas only (Cloudflare images reset 05:00 Tashkent). Never start a render while images are missing.
The spoken "subscribe" line (once, mid-video) is required in every script; the montage animation plays once,
on the scene that says it (`cta.plan`).

### Quality rules from the owner (2026-10-24, apply to every video)

- **Length: at least 10 minutes** (about 1,500 words, 70-95 scenes; `--minutes 10`). Shorter videos only if the owner asks.
- **Fact-check file for every video:** `scripts/<slug>.factcheck.md`, generated by the script builder (see `scripts/stone_age_24h.py`
  for the pattern: a `VERIFY` dict maps each source to how it was checked and how the wording stays honest). Every fact scene needs
  a reliable source found on the internet (paper, university/museum page, major science outlet, known book); open it before using it.
  If only a secondary summary was seen, hedge ("about", "according to"); drop what cannot be checked and list it under
  "Claims softened or dropped". Never invent a number.
- **Human voice:** write like a person talking, not a lecture: contractions, short and long sentences mixed, a joke or a personal
  take every few scenes, modern comparisons, honest "scientists disagree" moments. No filler, no hype, no false claims.
- **Montage:** the render already adds atmosphere effects (rain / snow particle loops, campfire light flicker, storm flashes;
  picked from the image prompt, none over indoor scenes: `services/atmosphere.py`, so write weather and fire into image prompts), camera moves, transitions, SFX, music with ducking and loudness balance, on-screen key
  numbers, a Subscribe animation (once, mid-video) followed by a Like animation, and one more Like animation in the last scene
  where the narrator says "like" (`cta.plan_likes`). Do not say "subscribe" in the last scene.
- **Chain:** when the owner asks for several videos, finish one completely (images, voice, render, kit) and move straight to the
  next without asking; write the next script while the worker renders (the worker runs one task at a time).

### Step 1: research and checks (before showing anything)

1. Turn the idea into 2-4 candidate English titles. Run
   `./venv/Scripts/python manage.py video_check "Title one" "Title two"`. It shows how close each is to
   videos already made, the hook of every earlier video, and the reference channels' most-viewed titles.
   A title marked TAKRORLANADI or a reused angle must be changed.
2. Research the facts with WebSearch/WebFetch. Every number, date, study and named finding needs a real,
   checkable source (peer-reviewed paper, university or museum page, well-known book). If a claim can't be
   verified, drop it or phrase it as uncertain ("researchers think", "evidence suggests"). Never invent
   statistics or studies.

### Step 2: the Uzbek concept (wait for approval)

Present in Uzbek, richer than the owner's idea:

- **Sarlavha**: the English title (curiosity question, under 60 characters, one CAPS keyword like the channel's
  other titles) + 4 alternatives, and why this angle can get recommended (point to reference-channel data).
- **Hook (0-40 s)**, the most important part: the 4 beats written out: (1) grab: drop straight into the topic
  (startling fact, number, scene in motion, sharp question), (2) **why watch**: why it matters to the viewer
  personally, right now, (3) **what they get**: a clear, specific promise of what they'll know or understand by the
  end, (4) an open loop answered later. Give every English hook line too, since the hook decides retention.
- **Tuzilma**: sections with approximate minutes; where the open loop is paid off.
- **Faktlar**: the key facts, each with its source and how certain it is.
- **Nimasi bilan farq qiladi**: how it differs from earlier videos (from `video_check`).
- **Monetizatsiya**: a short check against the rules below.

Do not write the English script until the owner approves (they may ask for changes first).

### Step 3: the English script

Write `scripts/<slug>.json` (schema below), save the owner's idea to `scripts/<slug>.idea.txt` and the approved
concept to `scripts/<slug>.concept.md`, then:

```
./venv/Scripts/python manage.py video_import scripts/<slug>.json --minutes N --idea scripts/<slug>.idea.txt --concept scripts/<slug>.concept.md --dry-run
./venv/Scripts/python manage.py video_import scripts/<slug>.json --minutes N --idea scripts/<slug>.idea.txt --concept scripts/<slug>.concept.md
```

The dry run must pass (fix the script, don't `--force`). The real import creates the project, runs the
director (emotion / camera / SFX / music marks via Gemini) and the compliance check. Fix any compliance warning
in the script and re-import with `--project <id>`. Then tell the owner (in Uzbek) the project link, the
hook, the structure and the check results. Images, voice and render are started by the owner in the UI.

### No human-from-apes content (owner's rule, 2026-11-08)

Never say or imply that humans descended from apes or share an ancestor with them: no "our line split from chimpanzees",
"cousins", "ape ancestor", "family tree of apes", "upgraded ape", "X million years before humans", and no image prompts
showing apes turning into humans. Animals may appear as animals (rats, dogs, apes playing), never as our relatives.
"Early humans" and history from archaeology are fine. Check every script for this before importing.

### Script rules (checked by `video_import`)

- Scenes = ~12 short hook scenes + (minutes x 60 - 35) / seconds_per_image (niche default 8 s), +-15%
  (`script.expected_scene_count`). Words ~= minutes x 150.
  If scenes > `MAX_IMAGES_PER_PROJECT` in `.env`, tell the owner before importing.
- Hook = the first ~30-40 s, written as ~12 scenes of ONE short sentence each (5-9 words, max 10, 2-3 s), so a new
  picture comes every 2-3 s; the render also cuts inside each picture every ~1.6 s (later scenes every ~4 s).
  All hook scenes have beat_type "hook"; together under ~110 words. The 4 beats above must all be there.
  Never open with a greeting, the channel name or "in this video".
  **Within the first 30-40 s the narrator must say outright (in two separate hook lines) WHY the viewer should stay
  (a personal stake: "Because the answer may explain...", "If you hate winter...") and WHAT they will get by the end
  ("By the end, you'll know / judge / be able to..."). Every script, no exception; the owner requires it for retention.
  Vary the opener: `video_check` lists every earlier hook, and most begin with "Imagine..." or "Have you ever...".
  Open the new one differently (a startling fact, a number, a scene already in motion, a bold claim, a short
  line of dialogue) so the channel doesn't feel templated.
- `scene_kind` strictly alternates hero, fact, hero, fact... starting with hero.
  - hero: the recurring main character acts out the idea. The image prompt contains "the main character".
  - fact: no main character. Shows the evidence or event (finding, artefact, fossil, animal, place, other people,
    a diagram without letters). The narration states a concrete, sourced fact. `fact_source` is filled in
    (short citation). Never write "the main character" in a fact scene's image prompt.
- Every scene serves the topic; no drifting side lessons. A clear narrative arc: hook, rising questions, reveals
  (`punchline`), the open loop paid off, a thoughtful ending (no generic "subscribe"; the app adds a subscribe
  animation itself).
- **Warm connection with the viewer (every script, owner's rule):** (1) once in the middle, in the hero scene right
  after a fact, a friendly invitation that contains the word "subscribe" and a "stay with me / we'll keep exploring
  together" promise, e.g. "Quick pause. If you're enjoying this, subscribe and stay with me. We'll keep exploring the
  ancient world together, one question at a time. It's free, it takes one second, and it helps more curious people find
  us." The montage animation plays once, on that scene. (2) The last scene thanks the viewer personally ("Thank you for
  spending these minutes with me"), asks for a like and a comment ("I read every one"), teases the next video and ends
  with a warm sign-off ("See you there, friend"). Do not repeat the word "subscribe" in the last scene.
- Voice: conversational, contractions, varied sentence length, light humour, at least one personal-take line
  and several modern-life comparisons. Avoid AI-sounding filler ("delve", "fascinating journey", "it's important
  to note", "in today's world"). Spell numbers as words where the narrator says them ("twenty fifteen").
- Image prompts: what is visible only, under 40 words, no style words, no text or letters in the picture.
- Voice acting (ElevenLabs v3 reads audio tags from `emotion`): YOU choose it per scene in the script JSON, so the tone
  follows the meaning of the line. Fields `emotion` (neutral, curious, excited, happy, funny, scared, tense, sad, awe,
  whisper, serious), `intensity` 1-3, `pace` (slow | normal | fast), `pause_after_ms` (0-1500, reveals and jokes only).
  Rules: never more than 3 scenes in a row with the same emotion; hook starts tense/curious, the "why watch" beat is
  serious or excited, the promise is curious, the open loop is whisper or tense; a reveal gets awe + a pause; jokes get
  funny + fast. Scenes with an `emotion` are not overwritten by the Gemini director (it still does camera/SFX/music).
  Write numbers as words, avoid ALL CAPS words and long dashes in narration (they change how v3 reads).
- `beat_type`: hook | build | punchline | normal. `sfx_cue` (sparingly, ~1 in 5): whoosh, ding, riser, pop, boing,
  swoosh, impact, click. `mood`: calm, mysterious, playful, tense, wholesome, epic, sad, quirky.
- No reused sentences: overlap with any earlier script above `MAX_SCRIPT_OVERLAP` (8% of 5-word phrases) blocks
  the import.

### JSON schema (`apps/videos/services/script.py: ScriptOut`)

```json
{
  "title": "What Did Ancient Humans Do All NIGHT?",
  "title_alternatives": ["...", "...", "...", "...", "..."],
  "description": "Two short paragraphs.\n\nSources:",
  "tags": ["8-12 search tags"],
  "mood": "mysterious",
  "sources": ["Author, A. (Year). Title. Journal."],
  "scenes": [
    {"narration": "...", "image_prompt": "The main character ...", "beat_type": "hook",
     "sfx_cue": null, "scene_kind": "hero", "fact_source": null},
    {"narration": "...", "image_prompt": "An ancient skull ...", "beat_type": "hook",
     "sfx_cue": null, "scene_kind": "fact", "fact_source": "Brain (1981), The Hunters or the Hunted?"}
  ]
}
```

## Hook video (Google Flow / Veo)

The hook (beat_type "hook" scenes, ~35 s) can be real moving clips; the rest stays pictures + transitions + SFX.
Project page -> "Flow promptlari": first draw the hook pictures, then in Flow use *Frames to video* with each picture
as the start frame and the prompt from the "Hook uchun video" box, download the clips named `001.mp4`, `002.mp4`...
and upload them in the same page. The render uses the first 2-3 s of each clip (`Scene.video`, `services/hook_video.py`),
drops Veo's sound and keeps the app's narration, music and SFX.

Automatic Flow: `flow_extension/` (Chrome extension, see its README) takes the queue made by the buttons on that page
(`services/flow_queue.py`, `views_flow.py`, model `FlowJob`), types each prompt into Flow, downloads the result and
sends it back. Results are checked (images: Gemini hero check; videos: ffmpeg length / black / frozen), bad ones are
retried `FLOW_MAX_ATTEMPTS` times, then wait on the page as "Tekshiring". All Flow-page selectors are in
`flow_extension/selectors.js`; if Flow changes, the owner presses "Diagnoz" in the popup and you fix that file from
`tmp/flow_diagnose.json`.

## YouTube monetization (inauthentic content, clarified July 2026)

Not monetized: (1) generic, repetitive, template-based videos without a narrative arc or visible creativity;
(2) off-putting or distressing content built for engagement; (3) AI personas giving health, medical, legal or
financial guidance. So every video needs its own angle, a real story, the owner's idea behind it, and no advice
in those areas. Graphic violence or suffering stays brief and non-graphic. The compliance checklist (Qoidalar page)
includes a rule for this.

## Code map

- Script: `apps/videos/services/script.py` (schema, prompt for Gemini, `clean_script`, `save_script`)
- Director: `services/director.py`; compliance: `services/compliance.py`; originality: `services/originality.py`
- Images: `services/images.py` + `image_providers/`; voice: `services/voice.py` + `tts/`; word timings: `services/align.py`
- Per-scene voice delivery (emotion -> rate/pitch/volume): `services/voice_style.py`
- Render (ffmpeg): `services/render.py` (camera moves, jump-cut shots, transitions, hook sound design, music cues,
  vignette, .srt); captions: `services/subtitles.py`; on-screen text + count-up stats: `services/overlays.py`
  (font `static/fonts/BebasNeue-Regular.ttf`, OFL); subscribe animation: `services/cta.py`
- `on_screen_text` works best as a number or short key phrase ("200,000 YEARS", "80%", "18 MINUTES"): numbers count
  up on screen and percentages fill a bar. Keep it rare (the director caps it at ~1 in 6 scenes).
- Background jobs: `apps/videos/tasks.py` (django-q2); assets in parallel: `services/assets.py`

## graphify

Run graphify as `D:/tools/graphify/Scripts/python.exe -m graphify ...` (the graphify.exe launcher is blocked by Smart App Control). This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

## Dubbed audio: Spanish, French (since 2026-11-10)

Every finished English video automatically gets es / fr audio tracks (Russian was dropped by the owner the same day) and translated titles + description
(`services/dub.py`, called at the end of `tasks.produce_video`; `settings.DUB_LANGUAGES`, `DUB_AUTO`). Narration is
translated by Google's free web translator, voiced with free Edge TTS male voices (Alvaro, Henri), sped up per scene
to fit the English timing and mixed with the same SFX and music. Files: `media/projects/p<id>/dub/<lang>.m4a` + `<lang>.json`,
shown on `/videolar/<id>/`; the owner uploads them in YouTube Studio -> Tillar -> Audio. When making the kit, ALSO write
`scripts/translations/p<id>.<lang>.json` with `{"titles": [3 hand-translated titles]}` (machine titles are weak); a
hand-written `"lines"` list (one per scene) replaces the machine narration. Videos are rendered WITHOUT burned-in
subtitles (captions=False) so the picture fits every audio language; the English .srt is still written next to the video.

## Video history (since 2026-11-10)

`reports/video_history.md` (+ `.json`) holds a short summary of every finished video: summary, chapters, hook, sources
(first author + year), keywords (`services/history.py`). It is rewritten by every `video_kit` and by `manage.py video_history`
(`--check "topic"` compares a candidate). `video_check` prints overlaps with it ("MAZMUN TAKRORI?" at 50%+) and
`video_import` warns when a new script reuses an earlier video's studies, repeats a hook opener or covers the same content.
Read the matching history entries before writing a concept; reusing a study is allowed only for a clearly different angle.

## Monetization check (since 2026-11-01)

Every video is checked against YouTube monetization rules in `niches/monetization_rules.json` (`services/monetization.py`,
`manage.py monetization_check --all|--music N|--project N`). It runs automatically after a render, in `music_new` and in
`video_kit`; results are saved to `media/monetization/` and shown on the music page. A scheduled task (every Monday 10:00)
refreshes the rules from the web, re-checks all videos and writes trend/evergreen topics per niche to `reports/weekly_<date>.md`.
Fix any `fail` before publishing; never put health promises ("cure", "melatonin", "100%") or advice in titles.
