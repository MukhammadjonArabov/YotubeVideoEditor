# Graph Report - YotubeVideo  (2026-11-10)

## Corpus Check
- 280 files · ~463,776 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 2114 nodes · 4568 edges · 138 communities (98 shown, 40 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 284 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- htmx.min.js
- gemini_client.py
- flow_queue.py
- cta.py
- pathlib
- video_import.py
- overlays.py
- align.py
- synthesize
- ImageProviderNotConfigured
- music_video.py
- test_images.py
- tasks.py
- Project
- media_library.py
- topics.py
- kit.py
- forms.py
- test_workflow.py
- overlays.py
- script.py
- Video tarixi
- Sources and checks
- django_conf
- history.py
- services/music_qc.py
- render_project
- policy_watch.py
- CloudflareImageProvider
- NamedFake
- render.py
- test_music.py
- test_manual_images.py
- test_director.py
- ImageProviderError
- views.py
- Sources and checks
- voice.py
- channel_research.py
- scenes.py
- models.py
- atmosphere.py
- generate_script
- check_project
- Sources and checks
- Sources and checks
- test_views.py
- Haftalik hisobot: 2026-11-02
- Sources and checks
- MontageV4Tests
- test_images.py
- Sources and checks
- MusicVideo
- Sources and checks
- TTSError
- Sources and checks
- django_db_models_deletion
- django_db
- load_kit
- ReplicateImageProvider
- Haftalik hisobot: 2026-11-09
- apps.py
- CommandBuilderTests
- ChannelSource
- hook_video.py
- music_new.py
- living.py
- SceneForm
- AutoExplainer (YotubeVideo)
- add_take
- music_tasks.py
- Niche
- .test_transition_planning
- os
- Musiqa: tinchlantiruvchi uzun musiqali videolar (20-30 daqiqa)
- video_check.py
- CharacterConsistencyTests
- What Would Ancient Humans Think of Our WORLD?
- A Day in the Life of an Early HUMAN
- When Did Ancient Humans First Get DRUNK?
- Who Performed the World's First SURGERY?
- How Did Ancient Humans Keep Food From ROTTING?
- How Did Ancient Humans Survive the ICE AGE Cold?
- What Could Ancient Humans Do That We CAN'T?
- Why Did Human BRAINS Shrink?
- Were Ancient Humans STRONGER Than Us?
- Who Cared for the INJURED 50,000 Years Ago?
- PolicyChangeNote
- ComplianceRule
- director.py
- video_history.py
- Could You Survive 24 Hours in the STONE AGE?
- 0008_scene_direction.py
- autoinstall.py
- ManagementCommandTests
- Fact-check: Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI)
- Fact-check: What Would Ancient Humans Think of Our WORLD?
- Fact-check: A Day in the Life of an Early HUMAN
- Why Can Humans Run for HOURS?
- Fact-check: What Could Ancient Humans Do That We CAN'T?
- Fact-check: Why Did Human BRAINS Shrink?
- Fact-check: Could You Survive 24 Hours in the STONE AGE?
- Fact-check: Were Ancient Humans STRONGER Than Us?
- plan
- The video workflow: idea -> concept -> approval -> script
- 0009_scene_sfx_list.py
- Fact-check: Why Can Humans Run for HOURS?
- 0004_seed_niche_policy.py
- ProjectMetaForm
- 0011_rule_inauthentic_2026.py
- 0012_rule_hook_promise.py
- 0005_character_reference.py
- Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI)
- 0006_consistent_character.py
- 0013_scene_hook_video.py
- 0016_project_flow_character.py
- manifest.json
- 0020_niche_settings.py
- ancient_memory.concept.md
- bad_news_brain.concept.md
- rainy_nights.concept.md
- stone_age_wood_age.concept.md
- stone_vs_today.concept.md
- laughter.concept.md
- test_render.py
- money_brain.concept.md
- broken_plans.concept.md
- conversation_mistakes.concept.md
- tiny_habits.concept.md

## God Nodes (most connected - your core abstractions)
1. `Project` - 124 edges
2. `Scene` - 48 edges
3. `render_project()` - 46 edges
4. `Niche` - 42 edges
5. `MusicVideo` - 42 edges
6. `Video tarixi` - 35 edges
7. `ImageProviderError` - 29 edges
8. `e()` - 29 edges
9. `ne()` - 28 edges
10. `ffmpeg_exe()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `11. Texnik tayyorgarlik (birinchi videodan oldin qilinadigan ishlar)` --references--> `Niche`  [INFERRED]
  niches/TeachAI.md → apps/videos/models.py
- `Script rules (checked by `video_import`)` --references--> `expected_scene_count()`  [INFERRED]
  CLAUDE.md → apps/videos/services/script.py
- `Hook video (Google Flow / Veo)` --references--> `FlowJob`  [INFERRED]
  CLAUDE.md → apps/videos/models.py
- `Quality rules from the owner (2026-10-24, apply to every video)` --references--> `plan_likes()`  [INFERRED]
  CLAUDE.md → apps/videos/services/cta.py
- `Monetization check (since 2026-11-01)` --references--> `fail()`  [INFERRED]
  CLAUDE.md → apps/videos/services/flow_queue.py

## Import Cycles
- 2-file cycle: `apps/videos/services/flow_queue.py -> apps/videos/tasks.py -> apps/videos/services/flow_queue.py`

## Communities (138 total, 40 thin omitted)

### Community 0 - "htmx.min.js"
Cohesion: 0.08
Nodes (100): A(), ae(), an(), at(), B(), be(), bn(), bt() (+92 more)

### Community 1 - "gemini_client.py"
Cohesion: 0.14
Nodes (14): _call(), _extract_json(), GeminiBusy, GeminiError, GeminiNotConfigured, generate_json(), run(), generate_text() (+6 more)

### Community 2 - "flow_queue.py"
Cohesion: 0.05
Nodes (32): FlowJob, Kind, Meta, Status, apply(), approve(), check_image(), claim_next() (+24 more)

### Community 3 - "cta.py"
Cohesion: 0.17
Nodes (9): ass_time(), CtaSound, events(), add(), add(), rounded_rect(), spoken_start(), subscribe_at() (+1 more)

### Community 5 - "video_import.py"
Cohesion: 0.09
Nodes (10): ProjectAdmin, SceneInline, Command, _text(), ComplianceCheck, Status, can_auto_approve(), run_check() (+2 more)

### Community 6 - "overlays.py"
Cohesion: 0.15
Nodes (8): ass_escape(), caption_events(), group_words(), proportional_timings(), scene_ass(), srt_for_scenes(), srt_time(), word_events()

### Community 7 - "align.py"
Cohesion: 0.06
Nodes (16): Command, _pump(), align(), AlignError, _decode(), _load_model(), map_to_script(), _norm() (+8 more)

### Community 8 - "synthesize"
Cohesion: 0.22
Nodes (3): enabled(), _align_words(), synthesize()

### Community 9 - "ImageProviderNotConfigured"
Cohesion: 0.20
Nodes (4): ImageProviderNotConfigured, parse_size(), SplitCloudflareProvider, SplitCloudflareTests

### Community 10 - "music_video.py"
Cohesion: 0.08
Nodes (23): _ass_sec(), audio_from_unit_cmd(), audio_loop_cmd(), block_cmd(), clip_audio_mean(), combine_cmd(), combine_takes(), cta_ass() (+15 more)

### Community 11 - "test_images.py"
Cohesion: 0.10
Nodes (9): Command, build_prompt(), character_reference_bytes(), draw_image(), ImageJob, mentions_main_character(), object_style(), scene_seed() (+1 more)

### Community 12 - "tasks.py"
Cohesion: 0.11
Nodes (14): scenes_waiting_for_flow(), apply_model(), needs_image(), _add_image_cost(), _elevenlabs_usable(), _generate_assets(), generate_images(), progress() (+6 more)

### Community 13 - "Project"
Cohesion: 0.08
Nodes (9): Command, Project, Meta, Status, maybe_auto_render(), is_navoiy(), enqueue(), AuthoredVoiceTests (+1 more)

### Community 14 - "media_library.py"
Cohesion: 0.09
Nodes (19): MusicTrack, Meta, SoundEffect, Meta, save_uploaded(), add_sfx(), add_track(), audio_duration() (+11 more)

### Community 15 - "topics.py"
Cohesion: 0.21
Nodes (6): find_similar(), find_similar_projects(), normalize_topic(), SimilarMatch, topic_hash(), TopicHashTests

### Community 16 - "kit.py"
Cohesion: 0.19
Nodes (12): badge(), cover(), design_hero(), design_object(), design_split(), find_character(), _font(), punch() (+4 more)

### Community 17 - "forms.py"
Cohesion: 0.09
Nodes (12): AudioUploadForm, ManualSuggestionForm, MultipleFileField, MultipleFileInput, NewProjectForm, NicheForm, Meta, PolicyDocumentForm (+4 more)

### Community 18 - "test_workflow.py"
Cohesion: 0.11
Nodes (9): Overlap, script_overlap(), shingles(), CheckScriptTests, OriginalityTests, scene(), script_json(), VideoCheckCommandTests (+1 more)

### Community 19 - "overlays.py"
Cohesion: 0.18
Nodes (9): _count_values(), events(), add(), font_dir(), _format_like(), percent_of(), _rect(), text_width() (+1 more)

### Community 20 - "script.py"
Cohesion: 0.10
Nodes (21): check_script(), alternation_ok(), authored_voice(), build_prompt(), clean_script(), count_ok(), expected_scene_count(), generate() (+13 more)

### Community 21 - "Video tarixi"
Cohesion: 0.06
Nodes (35): #10 Why Did Ancient Humans Paint CAVES?, #11 How Did Ancient Humans TALK Before Language?, #12 How Did Ancient Humans FIND Their Way?, #13 How Did Ancient Humans Taste DEATH in Plants?, #14 How Ancient Humans Spent Half Their Lives in the DARK, #17 Was the Stone Age Really a WOOD Age?, #18 How Did Ancient Humans Remember EVERYTHING Without Writing?, #19 Who Cared for the INJURED 50,000 Years Ago? (+27 more)

### Community 22 - "Sources and checks"
Cohesion: 0.12
Nodes (15): Blakemore, Wolpert & Frith (1998). Central cancellation of self-produced tickle sensation. Nature Neuroscience 1, 635-640, Bryant et al. (2016). Detecting affiliation in colaughter across 24 societies. PNAS 113, 4682-4687, Cai, Chen, White & Scott (2019). Modulation of humor ratings of bad jokes by other people's laughter. Current Biology 29, R677-R678, Claims softened or dropped, Davila Ross, Owren & Zimmermann (2009). Reconstructing the evolution of laughter in great apes and humans. Current Biology 19, 1106-1111, Dunbar et al. (2012). Social laughter is correlated with an elevated pain threshold. Proceedings of the Royal Society B 279, 1161-1167, Fact-check: Why Do Humans LAUGH?, Fact scenes (+7 more)

### Community 23 - "django_conf"
Cohesion: 0.10
Nodes (8): ImageProvider, ImageProviderError, build_chain(), FallbackImageProvider, get_provider(), _names(), preset_price(), provider_status()

### Community 24 - "history.py"
Cohesion: 0.11
Nodes (13): Command, build_entry(), _chapters(), finished_projects(), load_history(), script_reuse(), _source_key(), _summary() (+5 more)

### Community 25 - "services/music_qc.py"
Cohesion: 0.11
Nodes (11): Command, print_report(), analyze(), biggest_jump_db(), decode_mono(), edge_gap_db(), _ffmpeg(), loop_preview_cmd() (+3 more)

### Community 26 - "render_project"
Cohesion: 0.11
Nodes (15): delete_project_files(), project_media_dir(), capabilities(), concat_cmd(), concat_list(), ffmpeg_exe(), last_frame_cmd(), media_duration() (+7 more)

### Community 27 - "policy_watch.py"
Cohesion: 0.16
Nodes (11): PolicyDocument, check_all(), check_document(), clean_text(), diff_excerpt(), fetch_text(), PolicyFetchError, summarize_change() (+3 more)

### Community 28 - "CloudflareImageProvider"
Cohesion: 0.21
Nodes (5): CloudflareImageProvider, is_multipart_model(), CloudflareProviderTests, fake_png(), resp()

### Community 29 - "NamedFake"
Cohesion: 0.27
Nodes (3): is_quota_error(), FallbackChainTests, NamedFake

### Community 30 - "render.py"
Cohesion: 0.17
Nodes (14): clip_hash(), clip_shots(), ClipSpec, file_sig(), frame_count(), _kenburns(), _render_clip(), _run() (+6 more)

### Community 31 - "test_music.py"
Cohesion: 0.15
Nodes (8): save_music(), clip(), CommandTests, EndToEndTests, music_niche(), QualityTests, tone(), ViewTests

### Community 33 - "test_director.py"
Cohesion: 0.12
Nodes (17): enforce_rules(), d(), DirectorJobTests, EnforceRulesTests, scenes(), 10. Ishlash tartibi, 11. Texnik tayyorgarlik (birinchi videodan oldin qilinadigan ishlar), 1. Maqsad va tomoshabin (+9 more)

### Community 34 - "ImageProviderError"
Cohesion: 0.18
Nodes (3): Command, RunwareImageProvider, RunwareProviderTests

### Community 35 - "views.py"
Cohesion: 0.17
Nodes (8): _card(), _cover_url(), home(), _mmss(), _music_card(), niche_detail(), _niche_numbers(), video_detail()

### Community 36 - "Sources and checks"
Cohesion: 0.12
Nodes (15): Claims softened or dropped, Code of Hammurabi (c. 1754 BCE), laws on loans and interest; Mesopotamian loan tablets (silver about 20%, grain about 33%), Fact-check: Why Is Saving MONEY So Hard for Humans?, Fact scenes, Hublin et al. (2017). New fossils from Jebel Irhoud, Morocco and the pan-African origin of Homo sapiens. Nature 546, 289-292, Kahneman & Tversky (1979). Prospect theory. Econometrica 47; Tversky & Kahneman (1992). Advances in prospect theory. J. Risk and Uncertainty 5, Klapper, Lusardi & van Oudheusden (2015). Financial Literacy Around the World: S&P Global FinLit Survey (2014 Gallup data), Luttmer, E. (2005). Neighbors as negatives: relative earnings and well-being. Quarterly Journal of Economics 120, 963-1002 (+7 more)

### Community 37 - "voice.py"
Cohesion: 0.07
Nodes (15): AssetReport, produce(), draw(), report(), spent(), file_missing(), generate_scene_audio(), needs_audio() (+7 more)

### Community 38 - "channel_research.py"
Cohesion: 0.13
Nodes (14): ChannelAddForm, analyze_style(), _dt(), fetch_channel(), fetch_videos(), _get(), import_channel(), parse_channel_input() (+6 more)

### Community 39 - "scenes.py"
Cohesion: 0.08
Nodes (18): Scene, BeatType, CameraMove, Emotion, Meta, MusicCue, Pace, Status (+10 more)

### Community 40 - "models.py"
Cohesion: 0.06
Nodes (11): Command, Command, flow_result_path(), _project_dir(), project_video_path(), scene_audio_path(), scene_clip_path(), scene_image_path() (+3 more)

### Community 41 - "atmosphere.py"
Cohesion: 0.14
Nodes (7): _draw_loop(), effect_for(), fx_dir(), graph(), light_filter(), overlay_path(), check_video()

### Community 42 - "generate_script"
Cohesion: 0.18
Nodes (9): ComplianceResult, Finding, total_words(), generate_script(), fake_directions(), GenerateScriptTaskTests, _f(), f() (+1 more)

### Community 43 - "check_project"
Cohesion: 0.27
Nodes (10): worst_status(), check_music(), check_project(), _common(), _f(), _factcheck_for(), _hits(), rules() (+2 more)

### Community 44 - "Sources and checks"
Cohesion: 0.12
Nodes (15): Baumeister, Bratslavsky, Finkenauer & Vohs (2001). Bad is stronger than good. Review of General Psychology 5, 323-370, Brown, Imai, Vieider & Camerer (2021/2024), meta-analysis of loss aversion (lambda about 1.8-2.1); Gal & Rucker (2018), The loss of loss aversion, Journal of Consumer Psychology, Claims softened or dropped, Fact-check: Why Is Your Brain Addicted to BAD News?, Fact scenes, Ito, Larsen, Smith & Cacioppo (1998). Negative information weighs more heavily on the brain. Journal of Personality and Social Psychology 75, 887-900, Mather & Carstensen (2005). Aging and motivated cognition: the positivity effect in attention and memory. Trends in Cognitive Sciences 9, 496-502; Reed & Carstensen (2012), Frontiers in Psychology, Method (+7 more)

### Community 45 - "Sources and checks"
Cohesion: 0.12
Nodes (15): Claims softened or dropped, Dyble et al. (2019). Engagement in agricultural work is associated with reduced leisure time among Agta hunter-gatherers. Nature Human Behaviour 3, 792-796, Fact-check: Stone Age vs Today: Who Really Lived BETTER?, Fact scenes, Gurven & Kaplan (2007). Longevity among hunter-gatherers: a cross-cultural examination. Population and Development Review 33, 321-365, Hill et al. (2011). Co-residence patterns in hunter-gatherer societies show unique human social structure. Science 331, 1286-1289, Kaplan et al. (2017). Coronary atherosclerosis in indigenous South American Tsimane: a cross-sectional cohort study. The Lancet 389, 1730-1739, Method (+7 more)

### Community 46 - "test_views.py"
Cohesion: 0.13
Nodes (4): split_lines(), FlowPromptKitTests, png(), SlimSiteTests

### Community 47 - "Haftalik hisobot: 2026-11-02"
Cohesion: 0.18
Nodes (10): 1. Monetizatsiya qoidalari, 2. Videolarni qayta tekshirish (`monetization_check --all`), 3. Raqobatchilar va mavzular, (a) Qadimgi odamlar / inson hayoti fani, Asosiy ogohlantirishlar, (b) TeachAI (o'zbekcha), (c) Musiqa (Calm Hours), FAIL (2 ta) (+2 more)

### Community 48 - "Sources and checks"
Cohesion: 0.13
Nodes (14): Buehler, Griffin & Ross (1994). Exploring the 'planning fallacy'. Journal of Personality and Social Psychology 67, 366-381, Claims softened or dropped, Fact-check: Why Do We Make Plans We Never KEEP?, Fact scenes, Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement: a meta-analysis. Adv. Exp. Social Psychology 38; Sheeran et al. (2024) update, Hershfield et al. (2011). Neural measures of future self-continuity predict temporal discounting (Stanford/UCLA fMRI study), Method, Milne, Orbell & Sheeran (2002). Combining motivational and volitional interventions to promote exercise. British Journal of Health Psychology 7, 163-184 (+6 more)

### Community 49 - "MontageV4Tests"
Cohesion: 0.14
Nodes (5): motion_for(), motion_for_scene(), music_gain_expr(), zoompan_expr(), MontageV4Tests

### Community 50 - "test_images.py"
Cohesion: 0.14
Nodes (8): normalize_to_1080p(), AutoInstallTests, ImageCostTests, img_bytes(), ReplicateProviderTests, png(), ImageNormalizeTests, SceneViewTests

### Community 51 - "Sources and checks"
Cohesion: 0.14
Nodes (13): Boothby, Cooney, Sandstrom & Clark (2018). The liking gap in conversations: do people like us more than we think? Psychological Science 29, 1742-1756, Claims softened or dropped, Derber, C. (1979; 2000). The Pursuit of Attention: Power and Ego in Everyday Life. Oxford University Press, Fact-check: Conversation Mistakes You Don't Know You're MAKING, Fact scenes, Huang, Yeomans, Brooks, Minson & Gino (2017). It doesn't hurt to ask: question-asking increases liking. JPSP 113, 430-452, Kardas, Kumar & Epley (2022). Overly shallow? Miscalibrated expectations create a barrier to deeper conversation. JPSP 122, 367-398, Mastroianni, Gilbert, Cooney & Wilson (2021). Do conversations end when people want them to? PNAS 118, e2011809118 (+5 more)

### Community 52 - "MusicVideo"
Cohesion: 0.15
Nodes (26): MusicClip, Meta, MusicVideo, Meta, Status, enqueue(), _int(), _loop_preview_url() (+18 more)

### Community 53 - "Sources and checks"
Cohesion: 0.14
Nodes (13): Amabile & Kramer (2011). The Progress Principle. Harvard Business Review Press (about 12,000 diary entries from 238 people), Arithmetic illustration: 1.01^365 is about 37.8 and 0.99^365 is about 0.03 (a comparison, not a study), Claims softened or dropped, Fact-check: Why Tiny Daily Habits Beat MOTIVATION, Fact scenes, Galla & Duckworth (2015). More than resisting temptation: beneficial habits mediate the relationship between self-control and positive life outcomes. JPSP 109, 508-525, Gollwitzer & Sheeran (2006). Implementation intentions and goal achievement. Advances in Experimental Social Psychology 38, Hagger et al. (2016). A multilab preregistered replication of the ego-depletion effect. Perspectives on Psychological Science 11, 546-573 (+5 more)

### Community 54 - "TTSError"
Cohesion: 0.10
Nodes (10): TTSError, TTSProvider, TTSResult, WordTiming, ElevenLabsProvider, take_is_sane(), GeminiTTSProvider, get_tts() (+2 more)

### Community 55 - "Sources and checks"
Cohesion: 0.14
Nodes (13): Claims softened or dropped, Fact-check: Why Were Rainy Nights So DEADLY for Ancient Humans?, Fact scenes, Kjellberg Grahn et al. (2015). Protection against cold in prehospital care: wet clothing removal or addition of a vapor barrier. Wilderness & Environmental Medicine 26, 11-20, Method, Nadel et al. (2004). Stone Age hut in Israel yields world's oldest evidence of bedding. PNAS 101, 6821-6826, Parmeggiani (1960s onward), reviewed in Frontiers in Physiology (2017), 'Sleep and thermoregulation' (shivering and panting are suppressed in REM sleep; mostly animal data), Princeton University Outdoor Action, 'Hypothermia and cold weather injuries' (water conducts heat about 25 times faster than air; a field-guide rule of thumb) (+5 more)

### Community 56 - "django_db_models_deletion"
Cohesion: 0.15
Nodes (6): Migration, Migration, Migration, Migration, Migration, Migration

### Community 57 - "django_db"
Cohesion: 0.15
Nodes (6): Migration, Migration, Migration, Migration, Migration, Migration

### Community 58 - "load_kit"
Cohesion: 0.27
Nodes (5): build_previews(), kit_dir(), kit_url(), load_kit(), save_kit()

### Community 60 - "Haftalik hisobot: 2026-11-09"
Cohesion: 0.18
Nodes (10): 1. Monetizatsiya qoidalari, 2. Videolarni qayta tekshirish, 3. Raqobatchilar va mavzular (vidIQ outliers, oxirgi oy, <200K obunachi), (a) Qadimgi odamlar / inson hayoti fani, Asosiy ogohlantirishlar, (b) TeachAI (o'zbekcha), (c) Musiqa (Calm Hours), Eng yaxshi tanlov (+2 more)

### Community 61 - "apps.py"
Cohesion: 0.22
Nodes (3): VideosConfig, ensure_schedule(), ensure_policy_schedule()

### Community 62 - "CommandBuilderTests"
Cohesion: 0.24
Nodes (4): db_to_gain(), scene_sfx_items(), SfxHit, CommandBuilderTests

### Community 63 - "ChannelSource"
Cohesion: 0.13
Nodes (10): ChannelSource, Meta, State, SuggestedTopic, Meta, Status, suggest_topics(), is_configured() (+2 more)

### Community 64 - "hook_video.py"
Cohesion: 0.09
Nodes (19): enqueue(), hook_scenes(), match_files(), prompt_rows(), prompts_txt(), video_prompt(), VideoMatch, clean_character_name() (+11 more)

### Community 65 - "music_new.py"
Cohesion: 0.31
Nodes (4): check_spec(), Command, music_niche(), mvs_max_clips()

### Community 66 - "living.py"
Cohesion: 0.31
Nodes (4): frames(), loop_path(), _make(), masks()

### Community 67 - "SceneForm"
Cohesion: 0.29
Nodes (3): SceneForm, Meta, _sfx_choices()

### Community 68 - "AutoExplainer (YotubeVideo)"
Cohesion: 0.18
Nodes (10): Assumptions (so far), AutoExplainer (YotubeVideo), Images: Cloudflare Workers AI (free), Pages, Run, Setup (Linux), Setup (Windows, PowerShell), Speed & professional edit (render v2) (+2 more)

### Community 69 - "add_take"
Cohesion: 0.29
Nodes (4): MusicTake, Meta, add_take(), select_take()

### Community 70 - "music_tasks.py"
Cohesion: 0.12
Nodes (8): generate_takes(), _progress(), render_video(), build_prompt(), compose_music(), loop_plan(), plan_ctas(), PlanTests

### Community 72 - ".test_transition_planning"
Cohesion: 0.29
Nodes (3): plan_transition(), transition_duration(), transition_sfx_tag()

### Community 74 - "Musiqa: tinchlantiruvchi uzun musiqali videolar (20-30 daqiqa)"
Cohesion: 0.22
Nodes (8): 1. Mahsulot, 2. Ish tartibi, 3. Musiqa prompti qoidalari (ElevenLabs Music), 4. Sifat nazorati (avtomatik + men), 5. Flow video promptlari qoidalari, 6. Saytdagi imkoniyatlar (Musiqa yo'nalishi), 7. Cheklovlar va xavfsizlik, Musiqa: tinchlantiruvchi uzun musiqali videolar (20-30 daqiqa)

### Community 76 - "CharacterConsistencyTests"
Cohesion: 0.12
Nodes (10): build_qa_prompt(), check_scene_image(), QAOut, QAResult, _small_jpeg(), generate_scene_image(), save_scene_image(), CharacterConsistencyTests (+2 more)

### Community 77 - "What Would Ancient Humans Think of Our WORLD?"
Cohesion: 0.25
Nodes (7): Faktlar, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~10 daqiqa), What Would Ancient Humans Think of Our WORLD?

### Community 78 - "A Day in the Life of an Early HUMAN"
Cohesion: 0.25
Nodes (7): A Day in the Life of an Early HUMAN, Faktlar, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~10 daqiqa)

### Community 79 - "When Did Ancient Humans First Get DRUNK?"
Cohesion: 0.25
Nodes (7): Faktlar va ishonchlilik, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~7 daqiqa, 57 sahna), When Did Ancient Humans First Get DRUNK?

### Community 80 - "Who Performed the World's First SURGERY?"
Cohesion: 0.25
Nodes (7): Faktlar va ishonchlilik, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~7 daqiqa, 57 sahna), Who Performed the World's First SURGERY?

### Community 81 - "How Did Ancient Humans Keep Food From ROTTING?"
Cohesion: 0.25
Nodes (7): Faktlar va ishonchlilik, Hook (0-40 s), How Did Ancient Humans Keep Food From ROTTING?, Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~8.3 daqiqa, 63 sahna)

### Community 82 - "How Did Ancient Humans Survive the ICE AGE Cold?"
Cohesion: 0.25
Nodes (7): Faktlar va ishonchlilik, Hook (0-40 s), How Did Ancient Humans Survive the ICE AGE Cold?, Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma

### Community 83 - "What Could Ancient Humans Do That We CAN'T?"
Cohesion: 0.25
Nodes (7): Faktlar, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~10 daqiqa), What Could Ancient Humans Do That We CAN'T?

### Community 84 - "Why Did Human BRAINS Shrink?"
Cohesion: 0.25
Nodes (7): Faktlar, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~10 daqiqa), Why Did Human BRAINS Shrink?

### Community 85 - "Were Ancient Humans STRONGER Than Us?"
Cohesion: 0.25
Nodes (7): Faktlar, Hook (0-40 s), Monetizatsiya, Nimasi bilan farq qiladi, Sarlavha, Tuzilma (~10.5 daqiqa), Were Ancient Humans STRONGER Than Us?

### Community 86 - "Who Cared for the INJURED 50,000 Years Ago?"
Cohesion: 0.25
Nodes (7): Faktlar va ishonchlilik, Hook (0-40 s), Monetizatsiya, Oldingi videolardan farqi, Sarlavha, Tuzilma, Who Cared for the INJURED 50,000 Years Ago?

### Community 87 - "PolicyChangeNote"
Cohesion: 0.33
Nodes (3): policy_banner(), PolicyChangeNote, Meta

### Community 88 - "ComplianceRule"
Cohesion: 0.33
Nodes (4): ComplianceRuleForm, Meta, ComplianceRule, Meta

### Community 89 - "director.py"
Cohesion: 0.08
Nodes (13): apply(), build_prompt(), choices(), _clean(), direct(), DirectionOut, estimate_seconds(), _is_interrupt() (+5 more)

### Community 91 - "Could You Survive 24 Hours in the STONE AGE?"
Cohesion: 0.29
Nodes (6): Could You Survive 24 Hours in the STONE AGE?, Faktlar, Hook (0-40 s), Monetizatsiya, Sarlavha, Tuzilma (~10,5 daqiqa, 73 sahna)

### Community 95 - "Fact-check: Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI)"
Cohesion: 0.33
Nodes (5): Fact-check: Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI), Faktli sahnalar, Tashlangan yoki yumshatilgan da'volar, Ustozlik va inson ovozi (bajarilgan), Usul

### Community 96 - "Fact-check: What Would Ancient Humans Think of Our WORLD?"
Cohesion: 0.33
Nodes (5): Claims softened or dropped, Fact-check: What Would Ancient Humans Think of Our WORLD?, Fact scenes, Human-voice checklist (all done), Method

### Community 97 - "Fact-check: A Day in the Life of an Early HUMAN"
Cohesion: 0.33
Nodes (5): Claims softened or dropped, Fact-check: A Day in the Life of an Early HUMAN, Fact scenes, Human-voice checklist (all done), Method

### Community 98 - "Why Can Humans Run for HOURS?"
Cohesion: 0.33
Nodes (5): Faktlar va ishonchlilik, Hook (0-40 s), Monetizatsiya, Sarlavha, Why Can Humans Run for HOURS?

### Community 99 - "Fact-check: What Could Ancient Humans Do That We CAN'T?"
Cohesion: 0.33
Nodes (5): Claims softened or dropped, Fact-check: What Could Ancient Humans Do That We CAN'T?, Fact scenes, Human-voice checklist (all done), Method

### Community 100 - "Fact-check: Why Did Human BRAINS Shrink?"
Cohesion: 0.33
Nodes (5): Claims softened or dropped, Fact-check: Why Did Human BRAINS Shrink?, Fact scenes, Human-voice checklist (all done), Method

### Community 101 - "Fact-check: Could You Survive 24 Hours in the STONE AGE?"
Cohesion: 0.33
Nodes (5): Claims softened or dropped, Fact-check: Could You Survive 24 Hours in the STONE AGE?, Fact scenes, Human-voice checklist (all done), Method

### Community 102 - "Fact-check: Were Ancient Humans STRONGER Than Us?"
Cohesion: 0.33
Nodes (5): Claims softened or dropped, Fact-check: Were Ancient Humans STRONGER Than Us?, Fact scenes, Human-voice checklist (all done), Method

### Community 103 - "plan"
Cohesion: 0.18
Nodes (7): enabled(), like_events(), plan(), plan_likes(), SubscribeCtaTests, Autonomous mode ("mavzu top"), Quality rules from the owner (2026-10-24, apply to every video)

### Community 104 - "The video workflow: idea -> concept -> approval -> script"
Cohesion: 0.25
Nodes (8): JSON schema (`apps/videos/services/script.py: ScriptOut`), No human-from-apes content (owner's rule, 2026-11-08), Script rules (checked by `video_import`), Step 1: research and checks (before showing anything), Step 2: the Uzbek concept (wait for approval), Step 3: the English script, The site is read-only (since 2026-10-23), The video workflow: idea -> concept -> approval -> script

### Community 106 - "Fact-check: Why Can Humans Run for HOURS?"
Cohesion: 0.40
Nodes (4): Contested points told honestly in the script, Corrections made on 2026-10-24, Fact-check: Why Can Humans Run for HOURS?, Fact scenes

### Community 112 - "Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI)"
Cohesion: 0.50
Nodes (3): Faktlar, Sun'iy intellekt nima va u qanday ISHLAYDI? (TeachAI), Tuzilma (~9 daqiqa)

### Community 136 - "test_render.py"
Cohesion: 0.09
Nodes (14): EdgeTTSProvider, words_from_alignment(), AtmosphereTests, CaptionToggleTests, EdgeProviderTests, EndToEndRenderTests, synthesize(), synthesize() (+6 more)

## Knowledge Gaps
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Project` connect `Project` to `flow_queue.py`, `video_import.py`, `align.py`, `test_render.py`, `tasks.py`, `media_library.py`, `topics.py`, `forms.py`, `test_workflow.py`, `script.py`, `django_conf`, `history.py`, `NamedFake`, `test_manual_images.py`, `test_director.py`, `ImageProviderError`, `views.py`, `voice.py`, `channel_research.py`, `scenes.py`, `models.py`, `generate_script`, `check_project`, `test_views.py`, `test_images.py`, `ChannelSource`, `hook_video.py`, `CharacterConsistencyTests`, `director.py`, `ProjectMetaForm`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 70 inferred relationships involving `Project` (e.g. with `NewProjectForm` and `ProjectMetaForm`) actually correct?**
  _`Project` has 70 INFERRED edges - model-reasoned connections that need verification._
- **Should `htmx.min.js` be split into smaller, more focused modules?**
  _Cohesion score 0.07748319641523525 - nodes in this community are weakly interconnected._
- **Why does `Scene` connect `scenes.py` to `hook_video.py`, `flow_queue.py`, `SceneForm`, `views.py`, `voice.py`, `models.py`, `test_images.py`, `CharacterConsistencyTests`, `tasks.py`, `media_library.py`, `test_views.py`, `forms.py`, `test_images.py`, `script.py`, `director.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `Scene` (e.g. with `SceneForm` and `_transition_choices()`) actually correct?**
  _`Scene` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `gemini_client.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13846153846153847 - nodes in this community are weakly interconnected._
- **Why does `Niche` connect `Niche` to `video_import.py`, `test_render.py`, `forms.py`, `test_workflow.py`, `script.py`, `history.py`, `test_music.py`, `test_director.py`, `views.py`, `models.py`, `generate_script`, `test_views.py`, `test_images.py`, `MusicVideo`, `hook_video.py`, `music_new.py`, `CharacterConsistencyTests`, `PolicyChangeNote`, `ManagementCommandTests`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._