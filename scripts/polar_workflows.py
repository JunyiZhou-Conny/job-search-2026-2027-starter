#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from polar_policy import (
    APPLY_URL_CONFIDENCE,
    CONTROL_COLUMNS,
    CONTROL_REQUIRED_READBACK,
    DEGREE_LEVEL_REPEAT_KEY,
    HEARTBEAT_COLUMNS,
    INCIDENT_CATEGORIES,
    INCIDENT_LOG_COLUMNS,
    LEARNING_REPORTS_COLUMNS,
    LEASE_KEY,
    QUEUE_COLUMNS,
    REQUIRED_QUEUE_READBACK,
    RUN_LOG_COLUMNS,
    SCHEMA_TABS,
    TIME_LOST_CATEGORIES,
    WRITING_LOG_COLUMNS,
    apply_run_caps,
    bootstrap_prompt,
    csv_header,
    document_availability,
    needs_browser_lock,
    raw_runtime_url,
    raw_workflow_url,
    workflow_version,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / "generated" / "polar" / "workflows"
SCHEMA_DIR = ROOT / "generated" / "polar"

WORKFLOW_RENDERERS: Dict[str, Callable[[Dict[str, Any]], str]] = {}


def _register(name: str) -> Callable[[Callable[[Dict[str, Any]], str]], Callable[[Dict[str, Any]], str]]:
    def wrap(fn: Callable[[Dict[str, Any]], str]) -> Callable[[Dict[str, Any]], str]:
        WORKFLOW_RENDERERS[name] = fn
        return fn

    return wrap


def _lines(items: List[str]) -> str:
    return "\n".join(items)


def _header(name: str, operator: Dict[str, Any], version: str, status: str) -> str:
    schedules = operator.get("schedules") or {}
    schedule = {}
    for row in schedules.values():
        if isinstance(row, dict) and row.get("workflow") == name:
            schedule = row
            break
    cron = schedule.get("cron_et") or "manual"
    tz = operator.get("timezone") or "America/New_York"
    enabled = schedule.get("enabled", True)
    lock = "true" if needs_browser_lock(name) else "false"
    return _lines(
        [
            f"# {name}",
            "",
            f"workflow: {name}",
            f"workflow_version: {version}",
            f"status: {status}",
            f"enabled: {str(enabled).lower()}",
            f"needs_browser_lock: {lock}",
            f"schedule: {cron} {tz}",
            f"runtime_url: {raw_runtime_url()}",
            "COMPILED ARTIFACT. Not canonical.",
            "",
        ]
    ) + "\n"


def _open_files() -> str:
    return _lines(
        [
            "## Open these files",
            "",
            "1. This file. Follow it.",
            f"2. {raw_runtime_url()}",
            "",
            "Read both fully before clicking employer pages.",
            "Do not browse the rest of GitHub.",
            "",
        ]
    )


def _secrets_ban() -> str:
    return _lines(
        [
            "## Secrets ban",
            "",
            "Never write passwords, cookies, OTP codes, 2FA secrets, session tokens,",
            "street address values, or transcript contents into the Sheet, email, git, or a report.",
            "Phone and email values stay in the local Polar profile.",
            "",
        ]
    )


def _lease_block(name: str, operator: Dict[str, Any]) -> str:
    lease = operator.get("lease") or {}
    ttl = int(lease["ttl_minutes"])
    refresh = int(lease["refresh_if_remaining_below_minutes"])
    if not needs_browser_lock(name):
        return _lines(
            [
                "## Browser lease",
                "",
                "needs_browser_lock: false",
                f"This workflow does not take the {LEASE_KEY} lock.",
                "If apply-ready-jobs or discover-jobs-hourly holds the lock, continue anyway.",
                "",
            ]
        )
    return _lines(
        [
            "## Browser lease",
            "",
            "needs_browser_lock: true",
            f"lock_key: {LEASE_KEY}",
            f"ttl_minutes: {ttl}",
            "tab: control",
            "",
            "At start, locate the control row by the key cell polar_browser. Do not pick a visually empty row.",
            "If another non-expired production workflow owns it, write run_log result SKIPPED_LOCKED and exit.",
            f"If the lock is free or expired, acquire it with this run_id, this workflow, acquired_at now, and expires_at now plus {ttl} minutes.",
            "Immediately upsert a run_log row for this run_id with started_at now and result PARTIAL. Notes may say acquired.",
            "A later crash must still leave that run_log row. Update the same run_id at the end. Do not append a second row for the same run_id.",
            f"If this long run is still active and remaining time is under {refresh} minutes, refresh expires_at to now plus {ttl} minutes.",
            "After each job stage, refresh control notes with polar_policy.lease_checkpoint_notes(job_key, last_stage).",
            "Release the lock on normal completion by clearing owner_run_id. Keep the checkpoint until then.",
            "A crashed run must not lock the browser forever. Treat an expired expires_at as free.",
            "Do not weaken the lease to recover a crashed run.",
            "",
        ]
    )


def _sheet_write_contract() -> str:
    return _lines(
        [
            "## Sheet write contract",
            "",
            "mode: named_header_mapping",
            f"required_readback: {', '.join(REQUIRED_QUEUE_READBACK)}",
            "blank_policy: write_explicit_blank",
            f"never_omit: {APPLY_URL_CONFIDENCE}",
            "",
            "1. Read the actual header row of the tab you are writing.",
            "2. Build a field-name to column mapping from those headers.",
            "3. Write fields by header name, not by remembered position.",
            "4. If a value is empty, still write an explicit blank in that named column.",
            "5. Do not shorten a row and shift later fields left.",
            "6. After an important queue write, read back job_key, status, and last_stage.",
            "7. If those three fields do not match what you meant, repair the row before the next job.",
            "",
            "Control tab writes are key upserts.",
            "Locate the row by the key cell. Never choose a row because it looks empty on screen.",
            "If the target key is missing, append a new row.",
            "If the visible row has a different key, or no key, abort. Do not write that row.",
            "If two rows share the same key, abort.",
            "Commit the edit. Then reread "
            + ", ".join(CONTROL_REQUIRED_READBACK)
            + ".",
            "A cell that looked correct is not proof the write persisted. The reread is the proof.",
            "github_write_canary must never overwrite polar_browser.",
            "After a canary write, reread polar_browser key, owner_run_id, acquired_at, and expires_at.",
            "Those four cells must still match the values from before the canary write. Notes on that lock may change.",
            "These English rules are what Polar follows. polar_policy helpers are the same decision table for engineers.",
            "",
            "Omitting apply_url_confidence once shifted status and last_stage into the wrong columns.",
            "Named writes are the fix. Prose that says remember column I is not the fix.",
            "",
        ]
    )


def _telemetry_block(include_incidents: bool = True) -> str:
    lines = [
        "## Run telemetry",
        "",
        "One workflow invocation writes one run_log row.",
        "Copy workflow_version from this file into that row.",
        "Record started_at when you acquire work. Record ended_at before you exit.",
        "duration_minutes is coarse. Use whole minutes.",
        "result is SUCCESS, PARTIAL, FAILED, SKIPPED_LOCKED, or NO_WORK.",
        "",
    ]
    if include_incidents:
        lines.extend(
            [
                "Write an incident_log row when something material happens.",
                "Use one category from this list:",
                ", ".join(INCIDENT_CATEGORIES) + ".",
                "If minutes were lost, also set time_lost_category from:",
                ", ".join(TIME_LOST_CATEGORIES) + ".",
                "repeat_key groups recurrences. Examples: simplify_onboarding, queue_schema_shift, "
                + DEGREE_LEVEL_REPEAT_KEY
                + ".",
                "Degree-level hard gates that discovery missed use that one repeat_key. Do not invent phd_only_missed_at_discovery variants.",
                "incident_id is INC-YYYYMMDD-NNN on today's America/New_York date, three digits.",
                "The sequence is monotonic. Read existing values for that date. The next id is one more than the highest number.",
                "If 001 and 003 exist, write 004. Do not fill gaps. Never reuse one. Do not write INC-YYYYMMDD-01.",
                "01 and 001 count as the same number.",
                "A missing birth date or OPT-months answer is MISSING_FACT, not MISSING_DOCUMENT.",
                "For authorization widgets, record auth_outcome as answered, optional_left_blank, ambiguous_required_blocked, hard_eligibility_skip, or disclosure_prevented.",
                "durable_candidate is yes only when a repo policy or compiler change would prevent a repeat.",
                "Evidence must be enough for an engineer. No secrets.",
                "",
            ]
        )
    return _lines(lines)


def _identity_block() -> str:
    docs = document_availability()
    doc_lines = []
    for doc in docs:
        avail = "available" if doc.get("exists") else "missing"
        doc_lines.append(
            f"- {doc.get('id')}: path `{doc.get('approved_path')}` ({avail}). "
            f"Use when the form asks for that document class."
        )
    return _lines(
        [
            "## Local identities and documents",
            "",
            "street_address_source: local Polar or private profile. Never copy the street value into git or the Sheet.",
            "Normal ATS email, account email, preferred contact, and password-reset email use the local APPLICATION mailbox.",
            "If a field asks for school email, university email, or institutional email, use the local academic mailbox.",
            "A resume parser that pastes Harvard email into a normal contact field is wrong. Correct it before Submit.",
            "Do not create a second employer account only to change email.",
            "Do not write mailbox values or passwords into the Sheet.",
            "",
            "Approved documents:",
            *doc_lines,
            "Do not attach a transcript when the job asks for a different school or a diploma.",
            "If a required transcript is missing locally and in the registry, mark BLOCKED with category MISSING_DOCUMENT.",
            "Never paste transcript contents into logs.",
            "",
        ]
    )


@_register("discover-jobs-hourly")
def render_discover(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            _lease_block("discover-jobs-hourly", operator),
            _sheet_write_contract(),
            _telemetry_block(),
            "## Work order",
            "",
            "Never apply. Never click Submit. Never click Jobright APPLY WITH AUTOFILL.",
            "Never invent metrics, projects, employers, referrals, citizenship, or clearance.",
            "This run must finish quickly. Checkpoint the Sheet after every new or updated job.",
            "",
            "1. Create run_id. Read the control lock. Exit SKIPPED_LOCKED if blocked.",
            "2. Open Jobright while already logged in.",
            "3. Inspect Matches at https://jobright.ai/jobs/recommend.",
            "4. Inspect the intern and newgrad minisite boards listed in POLAR_RUNTIME section B.",
            "5. For each unseen card, write or update one queue row using named header mapping.",
            "6. job_key is the Jobright job id when the URL is https://jobright.ai/jobs/info/<id>.",
            "7. Deduplicate by job_key first, then company + role + location, then section K.",
            "8. Triage with section C. Hard skips become status SKIP.",
            "9. If a section K key matches, do not set READY_REGULAR or READY_PRIORITY.",
            "10. For KEEP rows that pass section K, set READY_REGULAR or READY_PRIORITY using section D.",
            "11. Set resume_cluster from section E.",
            "12. Keep Jobright source_url. last_stage stays discovered.",
            "13. Leave apply_url empty unless you already have a trusted employer URL.",
            "14. Always write apply_url_confidence. Use none when apply_url is empty.",
            "15. Do not open Original Job Post in this Workflow.",
            "16. Never start apply-ready-jobs work in this Workflow.",
            "",
            "Stop when the first loaded pages of the configured boards are covered.",
            "Do not infinite-scroll the whole internet.",
            "Write the run_log row. Release the lock.",
            "",
        ]
    )


@_register("apply-ready-jobs")
def render_apply(operator: Dict[str, Any]) -> str:
    caps = apply_run_caps()
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            _lease_block("apply-ready-jobs", operator),
            _sheet_write_contract(),
            _telemetry_block(),
            _identity_block(),
            "## Priority contract",
            "",
            f"max_new_jobs: {caps.max_new_jobs}",
            f"reserved_priority_slots: {caps.reserved_priority_slots}",
            "shared_pool: true",
            "reservation_is_from_pool: true",
            f"prioritized_auto_submit: {str(caps.prioritized_auto_submit).lower()}",
            "writing_log_required_before_priority_submit: true",
            "priority_submit_gate: polar_policy.priority_submit_permitted",
            f"max_regular_submissions_per_local_day: {caps.max_regular_submissions_per_local_day}",
            "",
            "Recovery first. Inspect every SUBMISSION_UNKNOWN row. Verify. Never blindly resubmit.",
            "Then resume the oldest IN_PROGRESS row from last_stage.",
            "If READY_PRIORITY exists, reserve 1 new-execution slot for one priority job.",
            "Use remaining new-execution slots for READY_REGULAR.",
            "If no READY_PRIORITY exists, regular may use every configured new-execution slot.",
            "Do not let a READY_REGULAR backlog starve READY_PRIORITY.",
            "",
            "## Simplify contract",
            "",
            "role: optional_accelerator",
            "max_attempts_per_application: 1",
            "fallback: polar_runtime_plus_local_profile",
            "",
            "Try Simplify once when it is already available and useful.",
            "If onboarding, missing injection, a broken session, or repeat navigation appears, stop using it on that job.",
            "Fall back to POLAR_RUNTIME, the approved resume or document registry, and the local Polar profile.",
            "Do not spend the run repairing Simplify.",
            "If Simplify materially slowed the run, write a PERFORMANCE incident with repeat_key simplify_onboarding or simplify_not_injected.",
            "",
            "## Apply-time hard eligibility",
            "",
            "Immediately after the employer JD is readable, before login, account creation, or form fill,",
            "skip PhD-only and undergraduate-only gates.",
            "Skip phrases include phd only, phd students only, phd candidates only, doctoral students only,",
            "must be pursuing a phd, must be enrolled in a phd, undergraduate students only,",
            "undergraduates only, and must be an undergraduate.",
            "Do not skip PhD preferred, PhD and Master's, or a sentence that says the role is not PhD only.",
            "Do not skip a line that only says the student must be enrolled in a degree.",
            "Master's study is not PhD and is not undergraduate-only.",
            "If the posting matches a skip phrase, status SKIP. Do not authenticate. Do not fill.",
            f"Incident repeat_key is {DEGREE_LEVEL_REPEAT_KEY}. Category TRIAGE.",
            "Also skip a 2026 role or start, employment start before 2027-01-18,",
            "a non-US work location, or an incompatible TS-SCI or polygraph requirement.",
            "If the page is an HTTP 404, says page not found, no longer open, no longer accepting,",
            "or that this job or requisition has been removed or closed, SKIP.",
            "A job id that contains the digits 404 is not a closed page. Barriers removed is not a closed page.",
            "Close the tab. Do not open a sibling requisition.",
            "Sponsorship unknown, unavailable, or generally not offered is not a skip.",
            "F-1 or OPT mentioned on a board is not a skip.",
            "An exclusive graduation window remains a note, not a skip.",
            "Do not change graduation-window policy.",
            "Do not move Original Job Post resolution into hourly discovery.",
            "",
            "## Employer requisition dedupe",
            "",
            "After Original Job Post or the employer application is resolved, capture the most stable identity:",
            "employer_requisition_id, canonical employer apply_url, and ats_job_id.",
            "Write those named fields. Keep apply_url_confidence.",
            "Compare against the Sheet and section K.",
            "If another row already points at the same employer requisition, keep one canonical row.",
            "Mark siblings SKIP with blocker duplicate employer requisition and the canonical job_key.",
            "Do not submit the same employer requisition twice.",
            "Do not create a second ledger.",
            "",
            "## Work order",
            "",
            "Never click Jobright APPLY WITH AUTOFILL.",
            "Never invent facts. If a required fact is missing, leave the widget and mark BLOCKED.",
            "A blocked job must not stall the batch.",
            "",
            "For each selected job:",
            "1. Set status IN_PROGRESS and bump attempt_count. Write updated_at now. Read back job_key, status, last_stage.",
            "2. Open apply_url when confidence is exact or strong. Otherwise open source_url and use Original Job Post.",
            "3. Confirm company and title match the queue row. If they do not match, BLOCKED or SKIP.",
            "4. If the posting is closed or 404, SKIP. Do not pick a sibling from the employer's current openings.",
            "5. Read the full employer JD now. Run the apply-time hard eligibility check before login or form work.",
            "6. Capture employer identity and run requisition dedupe. Then authenticate only if the job is still eligible.",
            "7. Authenticate with ordinary browser flows when asked. Account creation is normal work.",
            "8. Attach the resume_cluster from the row. Use Simplify at most once. Then read the visible widgets.",
            "9. Fill standing answers from section A. Correct a resume-parser Harvard email on a normal contact field.",
            "   Authorization and identity widgets use polar_policy.auth_form_action.",
            "   Classify the exact question. Answer only that semantic. Do not copy one fact into another field.",
            "   If the field is optional, leave it blank. Do not volunteer F-1, OPT, EAD, citizenship, or sponsorship.",
            "   Required future-sponsorship widget: Yes. Required H-1B-named widget: No.",
            "   Required citizenship: China. Required visa type: F-1. Required eligible-to-begin: Yes.",
            "   Required authorized-for-any-employer: Yes. Required EAD: No. Required OPT approval: No. Required OPT eligibility: Yes.",
            "   Required currently-authorized or sponsorship-to-begin: leave the field and mark BLOCKED on this job only when that fact is unknown.",
            "   If the form names F-1, J-1, or M-1 and clearly says answer Yes or answer No, follow that polarity.",
            "   If it says select Yes or No, or uses not or never with Yes, leave the field and mark BLOCKED on this job only.",
            "   Country-only lists and work-authorization-without-sponsorship wording: blank if optional, BLOCKED if required.",
            "   After autofill, correct invented citizenship, copied sponsorship answers, unasked F-1, or extra explanation.",
            "   Do not mention immigration in Why-us, motivation, cover letters, or other free response unless the prompt asked.",
            "   A blocked authorization field must not stop the rest of the batch.",
            "10. Write free-response answers from sections F and I. Prompt-faithful. Evidence-grounded.",
            "11. For every nontrivial free-response question, append one writing_log row with the exact question, the exact answer used, and a short evidence note.",
            "12. Regular row. Validate, Submit once, verify. SUBMITTED or SUBMISSION_UNKNOWN. Do not click Submit a second time.",
            "13. Prioritized row. Deeper JD and company-specific reasoning. Same evidence-bank ceiling. writing_log is mandatory for every meaningful custom question.",
            "    Apply polar_policy.priority_submit_permitted before Submit.",
            "    If any meaningful custom question is unanswered in writing_log, do not Submit. Mark BLOCKED.",
            "    A logged question with a blank answer or a blank evidence_note is a Submit blocker.",
            "    If writing_log is complete and final validation passes, Submit once and verify.",
            "    REVIEW_READY is only for a missing owner fact or an explicit hold. It is not the default for prioritized rows.",
            "14. If this environment cannot complete a required step after a normal attempt, status BLOCKED. Continue.",
            "15. Update the Sheet after every meaningful stage with named writes. Refresh the lease checkpoint notes.",
            "",
            "ATS family is only a note.",
            "Do not implement CAPTCHA bypass, fingerprint spoofing, or anti-abuse evasion.",
            "Update the same run_id run_log row, including submitted_regular, submitted_priority, simplify_attempted, and simplify_fallback_count.",
            "Release the lock.",
            "",
        ]
    )


@_register("daily-job-summary")
def render_summary(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            _lease_block("daily-job-summary", operator),
            _sheet_write_contract(),
            _telemetry_block(include_incidents=False),
            "## Work order",
            "",
            "Never apply. Never click Submit.",
            "Do not open employer forms unless you need to verify a SUBMISSION_UNKNOWN row already in the digest.",
            "",
            "Read today's rows from queue, writing_log, heartbeat, run_log, and incident_log.",
            "Email Junyi one digest for America/New_York today.",
            "",
            "The first visible section must be:",
            "",
            "PRIORITY APPLICATIONS SUBMITTED TODAY",
            "",
            "For each prioritized SUBMITTED row today, include company, role, confirmation,",
            "every meaningful custom question, the exact submitted answer, and the short evidence note.",
            "This is post-submit owner oversight. Do not hide creative answers.",
            "",
            "Then include:",
            "- other SUBMITTED rows, with company, role, and confirmation",
            "- REVIEW_READY rows that still need an owner fact",
            "- SUBMISSION_UNKNOWN rows that need owner eyes",
            "- BLOCKED rows and the blocker text",
            "- SKIP or closed rows",
            "- new account or auth friction, without secrets",
            "- writing used, as a short list plus the most important examples",
            "- heartbeat success or failure if a heartbeat row exists today",
            "- SKIPPED_LOCKED runs, if any",
            "",
            "Subject line: Polar daily job summary YYYY-MM-DD.",
            "If the Sheet is unreachable, say that in the email and stop.",
            "Write the run_log row.",
            "",
        ]
    )


@_register("production-learning-daily")
def render_learning(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            _lease_block("production-learning-daily", operator),
            _sheet_write_contract(),
            _telemetry_block(),
            "## Work order",
            "",
            "This workflow does not change GitHub policy.",
            "It does not apply. It does not click Submit.",
            "",
            "Read today's America/New_York rows from run_log, incident_log, writing_log, and queue.",
            "Group incidents by repeat_key.",
            "Write one sanitized Markdown report that covers:",
            "- repeated incidents",
            "- one-off UI issues",
            "- local-only facts",
            "- missing documents",
            "- candidate durable policy lessons",
            "- triage problems",
            "- queue or state bugs",
            "- dedupe problems",
            "- writing observations",
            "- performance bottlenecks, using time_lost_category and minutes_lost",
            "",
            "Sanitize before you persist. The report must never contain street address, private application email,",
            "phone, OTP, password, cookie, session token, transcript contents, or private auth material.",
            "Replace those with redaction tokens if they appear in source rows.",
            "",
            "Write the report into the learning_reports tab with publish_status sheet_only.",
            "If control key github_write_canary is success, you may also publish the same sanitized body",
            "as a GitHub Issue titled [Polar Production] YYYY-MM-DD. Otherwise keep it in the Sheet.",
            "Do not invent a GitHub write path that has not been proven.",
            "Write the run_log row.",
            "",
        ]
    )


@_register("polar-scheduler-heartbeat")
def render_heartbeat(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            "## Work order",
            "",
            "Mode: saved Workflow on the named local profile.",
            "This workflow does not take the polar_browser lock.",
            "",
            "Open https://example.com",
            "Confirm the page title contains Example Domain.",
            "Open the Polar Jobs Google Sheet tab heartbeat.",
            "Append one named row:",
            "- recorded_at: now, America/New_York",
            "- workflow: polar-scheduler-heartbeat",
            "- result: success",
            "- page_opened: https://example.com",
            "- notes: screen lock unknown to you. Write only what you can observe.",
            "",
            "If you cannot open the page or the Sheet, append result failure and a short note.",
            "Also write one run_log row with lock_result NOT_REQUIRED.",
            "Never apply. Never open Jobright. Never include secrets.",
            "",
        ]
    )


@_register("polar-github-write-canary")
def render_github_canary(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            _lease_block("polar-github-write-canary", operator),
            _sheet_write_contract(),
            "## Work order",
            "",
            "status: manual_canary",
            "Do not schedule this Workflow.",
            "Do not mutate production policy, YAML, or Polar runtime files.",
            "",
            "Create one harmless GitHub Issue in JunyiZhou-Conny/job-search-2026-2027-starter.",
            "Title: [Polar Canary] github-write-proof",
            "Body: Polar created this issue to prove it can write a sanitized GitHub artifact. No secrets.",
            "Labels are optional. Do not mention jobs, emails, or documents.",
            "",
            "If the Issue is created, upsert control key github_write_canary with notes success and the Issue URL.",
            "Locate that row by key. Never write into the polar_browser row.",
            "Commit the edit. Reread key and notes. GitHub issue existence is a second signal, not a substitute for the reread.",
            "Write run_log result SUCCESS.",
            "If GitHub refuses the write, upsert the same github_write_canary key with notes failure and a short reason.",
            "Write run_log result FAILED.",
            "Either way, stop. Do not retry in a loop.",
            "",
        ]
    )


@_register("chatgpt-production-review")
def render_chatgpt(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            "## Status",
            "",
            "status: disabled_until_proven",
            "Do not schedule this Workflow.",
            "Do not run it until github_write_canary is success and Junyi names the ChatGPT conversation.",
            "",
            "## Designed work order",
            "",
            "1. Open today's sanitized Polar Production GitHub artifact.",
            "2. Open the owner-designated ChatGPT conversation only if Polar Preferences already record it.",
            "3. If that conversation is missing, stop and write run_log result FAILED with notes chatgpt_context_missing.",
            "4. Ask ChatGPT to classify each incident into one-off, local-only, missing document, durable policy, triage, queue/state, dedupe, writing, performance, or no action.",
            "5. Ask for P0 durable fixes, P1 durable fixes, local-only actions, no-action items, and ONE Cursor-ready implementation prompt.",
            "6. Persist that review back to the same GitHub artifact as a comment only if the canary write path is proven.",
            "7. Never paste secrets into ChatGPT. Use the already sanitized report.",
            "",
        ]
    )


@_register("cursor-production-maintenance")
def render_cursor(operator: Dict[str, Any]) -> str:
    return _lines(
        [
            _open_files(),
            _secrets_ban(),
            "## Status",
            "",
            "status: disabled_until_proven",
            "Do not schedule this Workflow.",
            "Do not run it until the ChatGPT review path and Cursor browser handoff are proven.",
            "",
            "## Designed work order",
            "",
            "1. Open today's production report.",
            "2. Read the ChatGPT production review if present.",
            "3. Open Cursor Web or Cursor Agent only if Polar Preferences already record that target.",
            "4. Give Cursor the generated implementation prompt.",
            "5. Cursor must inspect current main, verify each claimed issue, change only durable lessons,",
            "   regenerate runtime and workflow artifacts, run tests, and open a PR.",
            "6. STOP BEFORE MERGE.",
            "",
            "No autonomous merge.",
            "Do not run gh pr merge.",
            "Do not click Merge pull request.",
            "Do not enable auto-merge.",
            "",
        ]
    )


@_register("polar-sheet-migration")
def render_migration(operator: Dict[str, Any]) -> str:
    tab_lines = []
    for tab, columns in SCHEMA_TABS.items():
        tab_lines.append(f"- {tab}: {', '.join(columns)}")
    return _lines(
        [
            _secrets_ban(),
            _sheet_write_contract(),
            "## Work order",
            "",
            "This is a one-time setup. Do not schedule it.",
            "Open the existing Polar Jobs Google Sheet.",
            "Preserve every current queue, writing_log, and heartbeat row.",
            "Do not rewrite existing cells except to add missing headers.",
            "",
            "Create a tab only when it is missing. The required tabs and exact headers are:",
            "",
            *tab_lines,
            "",
            "If queue already has rows, keep them.",
            "If queue is missing employer_requisition_id or ats_job_id, append those headers at the far right.",
            "Do not insert a column in the middle of existing queue data.",
            "If apply_url_confidence is missing from the live header, stop and tell Junyi. Do not guess positions.",
            "",
            "Seed one control row with key polar_browser and empty owner_run_id.",
            "Do not invent old run_log or incident_log history.",
            "",
            "Verify by reading each header row and comparing it to the lists above.",
            "Write run_log result SUCCESS with notes sheet_migration_ok when verification passes.",
            "",
        ]
    )


def render_workflow(name: str, operator: Dict[str, Any]) -> str:
    body_fn = WORKFLOW_RENDERERS[name]
    body = body_fn(operator).rstrip() + "\n"
    schedules = operator.get("schedules") or {}
    enabled = True
    for row in schedules.values():
        if isinstance(row, dict) and row.get("workflow") == name:
            enabled = bool(row.get("enabled", True))
    status = "production" if enabled else "disabled_until_proven"
    if name == "polar-github-write-canary":
        status = "manual_canary"
    if name == "polar-sheet-migration":
        status = "manual_once"
    version = workflow_version(
        str(operator.get("policy_revision") or "unknown"),
        name + "\n" + body,
    )
    return _header(name, operator, version, status) + body


def render_manifest(operator: Dict[str, Any], versions: Dict[str, str]) -> str:
    rows = [
        "# Polar workflow manifest",
        "",
        "COMPILED ARTIFACT. Not canonical.",
        "",
        f"policy_revision: {operator.get('policy_revision')}",
        f"runtime_url: {raw_runtime_url()}",
        "",
        "| Workflow | Status | Lock | Raw URL |",
        "|---|---|---|---|",
    ]
    for name in WORKFLOW_RENDERERS:
        url = raw_workflow_url(name)
        lock = "yes" if needs_browser_lock(name) else "no"
        rows.append(f"| `{name}` | see file | {lock} | {url} |")
    rows.extend(
        [
            "",
            "Saved Polar Workflows store only the bootstrap prompt from docs/automation/POLAR_WORKFLOWS.md.",
            "They open the raw main URL on each run.",
            "",
        ]
    )
    for name, version in versions.items():
        rows.append(f"- `{name}` workflow_version `{version}`")
    return "\n".join(rows).rstrip() + "\n"


def write_schema_csvs(root: Path = ROOT) -> List[Path]:
    written: List[Path] = []
    out_dir = root / "generated" / "polar"
    out_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "queue_schema.csv": QUEUE_COLUMNS,
        "writing_log_schema.csv": WRITING_LOG_COLUMNS,
        "heartbeat_schema.csv": HEARTBEAT_COLUMNS,
        "run_log_schema.csv": RUN_LOG_COLUMNS,
        "incident_log_schema.csv": INCIDENT_LOG_COLUMNS,
        "control_schema.csv": CONTROL_COLUMNS,
        "learning_reports_schema.csv": LEARNING_REPORTS_COLUMNS,
    }
    for filename, columns in mapping.items():
        path = out_dir / filename
        path.write_text(csv_header(columns), encoding="utf-8")
        written.append(path)
    return written


def write_workflows(operator: Dict[str, Any], root: Path = ROOT) -> Tuple[Dict[str, str], List[Path]]:
    out_dir = root / "generated" / "polar" / "workflows"
    out_dir.mkdir(parents=True, exist_ok=True)
    versions: Dict[str, str] = {}
    written: List[Path] = []
    for name in WORKFLOW_RENDERERS:
        text = render_workflow(name, operator)
        path = out_dir / f"{name}.md"
        path.write_text(text, encoding="utf-8")
        written.append(path)
        for line in text.splitlines():
            if line.startswith("workflow_version:"):
                versions[name] = line.split(":", 1)[1].strip()
                break
    manifest = out_dir / "WORKFLOW_MANIFEST.md"
    manifest.write_text(render_manifest(operator, versions), encoding="utf-8")
    written.append(manifest)
    return versions, written


def bootstrap_prompts() -> Dict[str, str]:
    return {name: bootstrap_prompt(name) for name in WORKFLOW_RENDERERS}
