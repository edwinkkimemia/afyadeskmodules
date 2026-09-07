# MODULE 18 — AI FOR THE MODERN MEDICAL VA
### AfyaDesk Remote Medical Careers Course | Responsible Productivity With Human Review & Privacy

**Estimated study time:** 8–10 hours (reading + prompt library + workflow build + verification drills)
**Prerequisites:** Modules 1–17 (terminology + EHR + privacy + zones you now accelerate with AI safely)
**What you will produce:** Prompt library (10 prompts) + AI-assisted workflow saving 5+ hrs/week with privacy gates + verification log + time-saved calc.

---

## Learning Objectives

By the end of this module, you will be able to:

1. Explain LLM fundamentals, strengths, hallucinations, and limits for healthcare admin.
2. Write Role-Task-Context-Format-Constraints prompts for email, summaries, checklists, research, Excel, EODs.
3. Apply 6 high-value uses (drafting, summarizing non-PHI, automation, BAA transcription, research, productivity) with verification.
4. Enforce human-in-loop: draft → verify facts/tone/SOP → clinician approval if clinical-adjacent → send via official channel → document.
5. Refuse forbidden uses (PHI in public AI, direct patient send, dosage/triage advice, time-zone trust without verification).
6. Use BAA-covered enterprise AI correctly with 100% critical verification + “verified by” note + retention wipe.
7. Build 1-page workflow with tool map, 3 prompts, privacy checkpoint, approval, time calc, risks/mitigations.
8. Catch hallucinations (doses, guidelines, phones, zones, follow-ups) with replay/official-source/EHR checks.
9. Protect privacy across prompts, uploads, audio, retention with de-identification or non-use decisions.
10. Report AI value (hours saved, errors caught, turnaround) for raises without breaching.

---

## 1. AI Fundamentals: Predictor, Not Clinician (Know Limits to Stay Employed)

LLMs predict likely next words from training, don’t understand patients, access live EHR/insurance, or know your SOP/version. Great at: drafting polite variants, reformatting lists to checklists/tables, brainstorming options, explaining public payer steps in plain English, Excel formulas from description, prioritizing bullet dumps into EODs, summarizing public articles (not patient charts). Terrible at: knowing Dr. Lee’s preferences, verifying Aetna auth status, calculating correct time zones across DST (often 1-hour off — always WorldTimeBuddy verify), giving safe triage/dosage (hallucinates contraindications), keeping PHI private (retains/logs in free tiers), citing real guidelines with correct year/dose/phone (invents convincingly).

Hallucinations to memorize: invented doses (“Lisinopril 50 mg daily” when audio said “lifestyle”), invented phones/links (“Call +1-555-0142” fake), invented follow-ups (“Return 2 weeks” not ordered), invented guidelines (“New ADA says stop metformin if...” — verify ada.org + clinician), invented zones (“10:30 ET = 3:30 EAT” wrong by 2 hrs — verify). Rule: AI proposes, official source + EHR + clinician disposes. Never “AI said so” to patient/manager/auditor — say “Verified via [portal/EHR/guideline + clinician approval date].”

Kenyan VA edge: English + clinical literacy lets you spot hallucinations faster than general VAs (“Amlodipine 500 mg? — 100× normal, flag”). Gap: over-trust due to speed thrill (“Wow, 10 emails in 2 min!”) → skip verification → filed error → dismissal. Discipline: 2-min verification per AI draft (facts? tone? SOP? zone? PHI-free prompt? approval needed?) saves career. Track verification time vs manual time — net saving 40–60% with safety, not 90% reckless.

Kenyan VA edge: English + clinical literacy lets you spot hallucinations faster than general VAs (“Amlodipine 500 mg? — 100× normal, flag”). Gap: over-trust due to speed thrill (“Wow, 10 emails in 2 min!”) → skip verification → filed error → dismissal. Discipline: 2-min verification per AI draft (facts? tone? SOP? zone? PHI-free prompt? approval needed?) saves career. Track verification time vs manual time — net saving 40–60% with safety, not 90% reckless.

---

## 2. Six High-Value VA Uses With Prompts That Work (No PHI in Public Prompts)

**Email drafting (biggest time-saver):** Prompt: “You are a medical admin assistant for US family practice. Draft 3 polite SMS reminder variants (<160 chars each), warm, include placeholders [Name] [Date Time Zones] [Link] [Callback], HIPAA-aware tone, no PHI, with Reply YES CTA. Constraints: grade-8 reading, no abbreviations, dual-zone placeholder.” → edit 2 min (add name/time/link, verify zone via WorldTimeBuddy, tone per US direct vs UK polite), send via Weave/EHR, log. Saves 30 min/day for 20 reminders. Never let AI send directly — you personalize + verify + send + log.

**Summarization (public only):** “Summarize this public Aetna prior-auth article [paste public URL text, no patient data] into 8-bullet SOP with owners/dates for Trello, plain English, include portal links + ETA + follow-up cadence.” Verify on official payer site (AI invents portal buttons) + supervisor approval before SOP adoption. Never summarize patient chart/Audio/EHR notes in public AI — manual in EHR or BAA tool only.

**Automation (SOP → checklist/board):** “Turn this referral SOP text [paste de-identified SOP, no names/DOBs] into Trello checklist with titles, owners (VA/nurse/doctor), due dates with zones, attachments list, and Definition of Done per card. Format markdown table.” Paste to board, assign, set due zones, test 1 card end-to-end. Saves 1 hr/week retyping + prevents missed steps.

**Transcription assist (BAA only):** EHR DAX/Abridge with signed BAA + training: “Transcribe verbatim with speakers + timestamps 30 sec, flag uncertain [inaudible + best guess + confidence], format SOAP per template, list meds/doses/allergies/plan separately for verification, do not infer diagnosis or invent follow-up.” Verify 100% critical by replay + drugs.com + EHR match + sense-check (MI + ibuprofen only? flag), 3-pass proofread, note “AI-assisted via [tool] verified by [Name date zone], 2 flags p2, ready for signature,” wipe local per retention. Never free Otter/Gemini/phone apps with PHI.

**Research (public comparison):** “Compare Athenahealth vs SimplePractice scheduling for 3-provider mental health (pros/cons/pricing/integrations) in table, cite vendor pages 2025–2026, flag limitations, no PHI.” Verify on vendor sites + G2 (AI pricing outdated) + ask peer using it. Use for proposals (“Recommend Jane for UK allied health due to...” with sources).

**Productivity (Excel/EOD/agenda):** “Write Excel formula to flag referrals >14 days red with =TODAY()-sent, and XLOOKUP to pull patient phone from roster by MRN, with explanation.” Test on mock data, document. “Turn these bullets [paste de-identified tasks, no names] into prioritized EOD with numbers + blockers + tomorrow top 3, concise manager style.” Edit + verify numbers against tracker (AI miscounts) + send. Saves 20 min/day.

Prompt formula tattoo: **Role (“You are...”) + Task (verb + deliverable) + Context (practice type, audience, no PHI) + Format (bullets/table/<160 chars/markdown) + Constraints (tone, grade level, zone placeholder, HIPAA-aware, no PHI, cite sources, flag uncertain).** Bad: “Summarize Jane Smith DOB... HIV...” (PHI breach). Good: “Draft generic template for requesting missing insurance from US patient, polite, HIPAA-aware, placeholders only, no PHI.” Library 10 prompts (3 email, 2 summary, 1 automation, 1 transcription, 1 research, 1 Excel, 1 EOD, 1 agenda) with before/after edits + verification notes = portfolio proof of responsible AI value.

Prompt formula tattoo: **Role (“You are...”) + Task (verb + deliverable) + Context (practice type, audience, no PHI) + Format (bullets/table/<160 chars/markdown) + Constraints (tone, grade level, zone placeholder, HIPAA-aware, no PHI, cite sources, flag uncertain).** Bad: “Summarize Jane Smith DOB... HIV...” (PHI breach). Good: “Draft generic template for requesting missing insurance from US patient, polite, HIPAA-aware, placeholders only, no PHI.” Library 10 prompts (3 email, 2 summary, 1 automation, 1 transcription, 1 research, 1 Excel, 1 EOD, 1 agenda) with before/after edits + verification notes = portfolio proof of responsible AI value.

---

## 3. Quality Control + Privacy Rules That Keep Contracts (Human-in-Loop Non-Negotiable)

Workflow 6 gates every AI draft: 1) De-identify prompt fully (placeholders [Name] [Date Zones] [Link], no DOB/MRN/photo/audio with PHI in public tools — when in doubt, don’t paste, handle manually in EHR), 2) Draft with AI (BAA-covered for sensitive, public for generic templates only), 3) Verify facts (dates? zones via WorldTimeBuddy? doses via drugs.com/EHR? phones via header? guidelines via official + year? SOP version? tone per US/UK?), 4) Clinician approval if clinical-adjacent (results wording, triage advice, med instructions — route with SBAR + “AI draft for review, please approve/edit” + hold send till signed), 5) Send via official channel (EHR/portal/Weave/Teams, not personal Gmail/WhatsApp) + log to chart + close task, 6) Document (“AI-assisted draft via [tool] verified [date zone] + approved by [clinician date] + sent [channel time] — MK”) + track time saved vs manual + errors caught.

Forbidden absolute: names/DOB/MRN/phones/photos/IDs/voice with PHI into ChatGPT/Gemini/Copilot free/free-tier transcribers/grammar checkers retaining data; uploading EHR PDFs to free summarizers; letting AI message patients directly without human send; acting on AI dosage/triage/zones without official + clinician verification; trusting AI “confident” tone (hallucinates politely). If employer provides Copilot/ChatGPT Team/Enterprise with signed BAA + training + retention/region documented in writing — use only that for sensitive, still verify 100% critical + note + wipe local per policy. Ask onboarding: “Which AI is BAA-covered and authorized for [transcription/summarization/drafting] in writing? Retention? Training opt-out? Storage region? Audit?” Document answer + policy version + annual refresher. Report suspected AI breach (pasted to wrong tool) in 1 hour per Module 8 card (contain/revoke, assess what/whom/how many, notify supervisor/IT, preserve logs, remediate + retrain). One paste to public = reportable breach + dismissal — 2-min de-identification check saves career.

Refuse unsafe AI requests professionally: “I can’t paste patient details into public AI per privacy law/BAA — to protect us both I’ll draft generically without PHI now (2 min) + personalize securely in EHR + verify + send via portal. For speed I’ve prepared placeholder template for your approval — shall I proceed securely?” + log request + refusal + secure alternative. Speed with safety beats insecure speed that ends contracts.

Refuse unsafe AI requests professionally: “I can’t paste patient details into public AI per privacy law/BAA — to protect us both I’ll draft generically without PHI now (2 min) + personalize securely in EHR + verify + send via portal. For speed I’ve prepared placeholder template for your approval — shall I proceed securely?” + log request + refusal + secure alternative. Speed with safety beats insecure speed that ends contracts.

---

## 4. Final AI Assignment: Workflow Saving 5+ Hours/Week With Human Review (Portfolio + Graded)

Design 1-page flowchart + SOP (draw.io/Miro) + tool map + prompt library 3 + privacy checkpoint + approval + time calc + risks. Example “Referral chase automation saving 6 hrs/week”: Sheet tracker with =TODAY()-sent overdue flags → AI drafts 3 follow-up variants (de-identified placeholders, no PHI) 10 min vs 60 min manual → VA personalizes in EHR with names/dates/zones/links verified via WorldTimeBuddy/header (20 min) → task board auto-reminders (Asana rules: overdue → assign + Slack nudge) → weekly report auto-chart (closure % + avg days) → human sends via portal + logs + closes. Time: manual 8 hrs → AI-assisted 2 hrs (draft 0.5 + verify/personalize 1 + review/send 0.5) = 6 hrs saved × $8 = $48/week = $2,400/year per VA. Privacy gates: no PHI in prompts (placeholders), BAA board/EHR only, clinician approval for clinical wording, verification checklist (facts? zones? tone? SOP? approval? channel? log?), wipe drafts per retention. Risks/mitigations: hallucinated dates/zones → WorldTimeBuddy verify + read-back; tone too casual for complaint → US/UK variant review + supervisor sign; over-reliance skipping verification → 2-min gate + peer audit 10% weekly; BAA confusion → onboarding doc + annual refresher + NEVER list signed.

Deliverables folder `AfyaDesk/Module18/`: flowchart PDF + SOP one-pager + 10-prompt library with before/after edits + verification notes + 2-week time log (manual vs AI-assisted per task with accuracy) + error log (hallucinations caught: dose/zone/phone/follow-up + how: replay/official/EHR/sense) + privacy checklist signed + supervisor approval screenshot + 300-word reflection (biggest save, nearest miss + gate that caught it, SOP improvement with data, next automation with guardrails). Pass: 5+ hrs saved proven with logs, 100% PHI-free public prompts (audit), 100% critical verified, approval documented, risks mitigated. Distinction: live demo 10 min (prompt → draft → verify → personalize → send mock + log) + Loom for Talent Profile “responsible AI” badge that earns $2/hr premium as practices pay for speed with safety.

---

## Common Mistakes That End AI Privileges (And Contracts)

“AI said so” to patient/manager/auditor without verification (hallucinated dose/zone/guideline filed → harm + liability — always cite official + clinician approval), pasting full inbox with names/DOBs to “clean up” in public AI (breach + dismissal + ODPC/HIPAA notice — de-identify or manual), trusting AI zone math (“10:30 ET = 3:30 EAT” off 2 hrs → 7-hour miss + 1-star — WorldTimeBuddy verify + read-back + written twin), letting AI auto-send to patients (wrong name/link/dose at scale — human send + log), asking AI triage/dosage to tell patient directly (unsafe + scope violation — escalate to clinician + safety net + document), no error log (same hallucination repeats monthly — log + SOP gate + share in huddle). Pin NEVER list + 6-gate checklist above desk for 90 days.

<!-- PART5: quiz, takeaways -->



