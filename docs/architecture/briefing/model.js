export const TRUTH = Object.freeze({
  production: "Live Polar policy on current main",
  designed: "Specified, not the default Polar path yet",
  unproven: "Written down. Not shown unattended",
  historical: "True in August 2026. Not the current loop",
  press: "Public writing. Not Polar telemetry",
  unknown: "Not in this repo",
});

export const CHAPTERS = [
  { id: "why", title: "Why" },
  { id: "loop", title: "The loop" },
  { id: "hour", title: "The hour" },
  { id: "job", title: "One job" },
  { id: "resume", title: "Resume" },
  { id: "learn", title: "Learn" },
  { id: "map", title: "Map" },
];

export const SCENES = [
  {
    id: "open",
    chapter: "why",
    kicker: "Polar briefing",
    title: "A local operator that applies for Junyi",
    lede: "GitHub holds the rules. Polar Local is the hands on his Mac. A Google Sheet holds the live queue. Cursor changes the repo and stops before merge.",
    truth: "production",
    blocks: [
      { kind: "line", items: ["GitHub main", "Polar Local", "Google Sheet", "human merge"] },
    ],
  },
  {
    id: "market",
    chapter: "why",
    kicker: "The market",
    title: "Entry-level seats are scarce. Volume is not.",
    lede: "Public 2026 writing still describes a tight new-grad and intern market. Mid-level postings recovered faster. Openings draw large applicant stacks. ATS filters and experience lines thin those stacks.",
    truth: "press",
    note: "Press, not Polar numbers. This repo does not know Polar production volume.",
    blocks: [
      { kind: "cards", items: [
        { t: "What the press says", d: "Junior hiring stayed slower than the mid-level recovery. Internship-to-return is a common door." },
        { t: "What that means here", d: "Junyi needs truthful volume on US intern and 2027 new-grad roles, not a second job board." },
        { t: "What we will not show", d: "funnel.csv and the July weekly review are not market conversion. The Sheet is not in git." },
      ]},
    ],
  },
  {
    id: "doing",
    chapter: "why",
    kicker: "What Junyi is doing",
    title: "Hourly discovery. Hourly apply. Human merge.",
    lede: "He is not clicking Jobright Apply all day. Polar reads a logged-in Jobright session, writes READY rows, then later that hour opens the real employer page.",
    truth: "production",
    blocks: [
      { kind: "cards", items: [
        { t: "Automatic today", d: "Discover, triage, fill, Submit on Polar Local once Copilot is present and the Sheet schema is ready." },
        { t: "Still his job", d: "Merge. Restore Copilot. Answer a missing private fact. Run the one-time Sheet migration." },
        { t: "Not this loop", d: "The August friends deck still says a human clicks Submit. That is history." },
      ]},
    ],
  },
  {
    id: "tools",
    chapter: "why",
    kicker: "Tools",
    title: "Six tools on the happy path",
    lede: "Each tool owns one job. Polar is not a second Simplify. The Sheet is not a second GitHub.",
    truth: "production",
    blocks: [
      { kind: "tools", items: [
        { name: "Jobright", role: "Logged-in matches and minisites. Original Job Post only." },
        { name: "Polar Local", role: "Production browser on the Mac. Hourly discover and apply." },
        { name: "Google Sheet", role: "Runtime queue, claims, logs. Not applications.csv." },
        { name: "Simplify Copilot", role: "Required on the employer ATS page. A simplify.jobs login is not proof." },
        { name: "GitHub main", role: "Canonical policy, evidence, compiled Polar English." },
        { name: "Cursor", role: "Engineer. PRs and tests. Cloud discovery is shadow." },
      ]},
    ],
  },
  {
    id: "loop",
    chapter: "loop",
    kicker: "The loop",
    title: "Behavior changes only after merge",
    lede: "Polar reads two raw main URLs per run. An open PR is not live. PREFERENCES.md is a thin inbox, not a second policy library.",
    truth: "production",
    blocks: [
      { kind: "flow", items: [
        "GitHub main",
        "Polar bootstrap",
        "Sheet runtime",
        "learning report",
        "Cursor PR",
        "human merge",
      ]},
    ],
  },
  {
    id: "clock",
    chapter: "hour",
    kicker: "Eastern Time",
    title: "Five scheduled workflows. Four of them never apply.",
    lede: "Independent Polar workflows may overlap. A crashed apply worker must not freeze heartbeat, discovery, or learning.",
    truth: "production",
    blocks: [
      { kind: "clock", items: [
        { et: ":00", name: "discover-jobs-hourly", does: "See jobs. Triage. READY labels. Never apply." },
        { et: ":05", name: "polar-scheduler-heartbeat", does: "Harmless page plus one heartbeat row." },
        { et: ":20", name: "apply-ready-jobs", does: "One worker. Budget 3. Claim, fill, Submit once." },
        { et: "21:30", name: "daily-job-summary", does: "One email. Prioritized SUBMITTED first." },
        { et: "22:00", name: "production-learning-daily", does: "Sanitized report. Does not change GitHub." },
      ]},
    ],
  },
  {
    id: "states",
    chapter: "job",
    kicker: "Queue status",
    title: "One status machine. last_stage is a checkpoint.",
    lede: "English names are the real symbols. Chinese on the maps is meaning, not a second vocabulary.",
    truth: "production",
    blocks: [
      { kind: "states", items: [
        { name: "NEW", meaning: "Seen. Not yet READY." },
        { name: "READY_REGULAR", meaning: "Keep. Fast truthful apply." },
        { name: "READY_PRIORITY", meaning: "Keep. Deeper writing, then Submit." },
        { name: "IN_PROGRESS", meaning: "This run owns the row via claim_run_id." },
        { name: "REVIEW_READY", meaning: "Missing owner fact or explicit hold." },
        { name: "SUBMITTED", meaning: "Clicked and verified." },
        { name: "SUBMISSION_UNKNOWN", meaning: "May have clicked. Verify. Never blind retry." },
        { name: "BLOCKED", meaning: "This job cannot finish. The worker continues." },
        { name: "SKIP", meaning: "Closed, ineligible, or duplicate requisition." },
      ]},
    ],
  },
  {
    id: "worker",
    chapter: "job",
    kicker: "apply-ready-jobs",
    title: "Trust, claim, Copilot, fill, Submit once",
    lede: "If Copilot is missing, Polar restores READY and stops the run. It does not fall back to hand clicking. The job stays valid. The environment is unhealthy.",
    truth: "production",
    blocks: [
      { kind: "flow", items: [
        "trust bootstrap",
        "schema check",
        "claim_run_id",
        "employer page",
        "Copilot PRESENT",
        "autofill once",
        "Submit once",
      ]},
    ],
  },
  {
    id: "weight",
    chapter: "job",
    kicker: "Weight",
    title: "Same truth. More writing on prioritized rows.",
    lede: "Polar Local may Submit both regular and prioritized rows. Cursor Cloud still stops for a review packet. Do not mix the two planes.",
    truth: "production",
    blocks: [
      { kind: "cards", items: [
        { t: "READY_REGULAR", d: "Prefer the Simplify resume. Autofill once. Short faithful answers. Submit when validation passes." },
        { t: "READY_PRIORITY", d: "Deeper JD work. writing_log on every meaningful custom question. Then Submit on Polar Local." },
        { t: "Cloud plane", d: "G2 Submit is closed. Prioritized Cloud rows still need a review packet." },
      ]},
    ],
  },
  {
    id: "resume",
    chapter: "resume",
    kicker: "Resume stack",
    title: "The bank is truth. The master is inventory.",
    lede: "Polar attaches the Simplify resume on the profile today. If that widget is empty it does not upload the two-page master. It marks REVIEW_READY with missing_production_resume.",
    truth: "production",
    note: "ai_infra_v1 exists on main. Polar is not wired to it. ROUTE is designed. VIP tailor is exceptional.",
    blocks: [
      { kind: "flow", items: [
        "evidence_bank.yaml",
        "two-page master",
        "BUILD family one-pager",
        "ROUTE",
        "Polar attach",
      ]},
      { kind: "cards", items: [
        { t: "Skills judge", d: "Philosophy, selection, narrative, framing, semantic review." },
        { t: "Python vetoes", d: "Provenance, forbidden claims, one-page compile, PDF page count." },
        { t: "VIP", d: "Full JD to a custom one-pager. Human approval. Not the default apply path." },
      ]},
    ],
  },
  {
    id: "learn",
    chapter: "learn",
    kicker: "Self-improvement",
    title: "Polar records. Cursor proposes. Junyi merges.",
    lede: "production-learning-daily writes a sanitized report. It does not change GitHub policy. ChatGPT review is compiled and disabled.",
    truth: "production",
    blocks: [
      { kind: "flow", items: [
        "Sheet logs",
        "daily report",
        "optional Issue",
        "Cursor PR",
        "human merge",
        "next bootstrap",
      ]},
    ],
  },
  {
    id: "use",
    chapter: "learn",
    kicker: "How to use it",
    title: "Leave the Mac on. Merge what is right.",
    lede: "Ordinary browser work is Polar work. Account creation and Why-us answers from the evidence bank are autonomous once the gates below are clear.",
    truth: "production",
    blocks: [
      { kind: "list", items: [
        "Install or restore Simplify Copilot when an employer page has no Copilot UI.",
        "Run polar-sheet-migration once if claim_run_id is missing or duplicated.",
        "Provide a genuinely missing private fact.",
        "Merge a Cursor PR. An open PR is not canonical.",
        "Do not treat the August friends deck as the current loop.",
      ]},
    ],
  },
  {
    id: "map",
    chapter: "map",
    kicker: "Six bands",
    title: "The poster, one column at a time",
    lede: "The mermaid poster is 14,000 pixels wide. This page is how to walk it. English on a node is the symbol. Chinese is meaning.",
    truth: "production",
    blocks: [{ kind: "bands" }],
  },
];

export const BANDS = [
  {
    id: "B1",
    title: "Control",
    meaning: "谁拥有什么",
    nodes: [
      { name: "GitHub main", meaning: "Canonical durable memory", kind: "process" },
      { name: "Polar Local", meaning: "Production browser", kind: "process" },
      { name: "Google Sheet", meaning: "Runtime / checkpoint", kind: "sheet" },
      { name: "PREFERENCES.md", meaning: "Local inbox, not policy", kind: "external" },
      { name: "Cursor", meaning: "Engineer. Stops before merge", kind: "process" },
      { name: "Junyi / Owner", meaning: "Merge and Copilot repair", kind: "human" },
    ],
  },
  {
    id: "B2",
    title: "Discovery",
    meaning: "发现 → READY",
    nodes: [
      { name: "Jobright", meaning: "Logged-in matches", kind: "external" },
      { name: "discover-jobs-hourly", meaning: ":00 ET. Never apply", kind: "process" },
      { name: "NEW", meaning: "Seen", kind: "state" },
      { name: "READY_REGULAR", meaning: "Ordinary execute", kind: "state" },
      { name: "READY_PRIORITY", meaning: "Deeper writing", kind: "state" },
      { name: "SKIP", meaning: "Remote, non-US, 2026 start, PhD-only", kind: "state" },
    ],
  },
  {
    id: "B3",
    title: "Workers",
    meaning: "无全局锁",
    nodes: [
      { name: "apply-ready-jobs", meaning: "One worker. Budget 3", kind: "process" },
      { name: "claim_run_id", meaning: "Owns one job_key", kind: "process" },
      { name: "already_claimed", meaning: "Lost race. No budget spent", kind: "state" },
      { name: "polar_browser", meaning: "Historical only. Not a mutex", kind: "hist" },
    ],
  },
  {
    id: "B4",
    title: "ATS",
    meaning: "雇主申请页",
    nodes: [
      { name: "Original Job Post", meaning: "Never APPLY WITH AUTOFILL", kind: "process" },
      { name: "Copilot PRESENT", meaning: "Autofill once", kind: "decision" },
      { name: "MISSING / UNKNOWN", meaning: "Restore READY. Owner action", kind: "human" },
      { name: "Submit once", meaning: "Then verify", kind: "process" },
    ],
  },
  {
    id: "B5",
    title: "Persist + learn",
    meaning: "提交与改进",
    nodes: [
      { name: "SUBMITTED", meaning: "Verified success", kind: "state" },
      { name: "SUBMISSION_UNKNOWN", meaning: "Verify before retry", kind: "state" },
      { name: "production-learning-daily", meaning: "Sanitized report", kind: "process" },
      { name: "human merge", meaning: "Only gate into main", kind: "human" },
    ],
  },
  {
    id: "B6",
    title: "Workflows",
    meaning: "全部工作流",
    nodes: [
      { name: "discover-jobs-hourly", meaning: "Scheduled :00", kind: "process" },
      { name: "apply-ready-jobs", meaning: "Scheduled :20", kind: "process" },
      { name: "polar-sheet-migration", meaning: "Manual once", kind: "hist" },
      { name: "chatgpt-production-review", meaning: "Disabled", kind: "hist" },
    ],
  },
];

export function sceneIndex(id) {
  return SCENES.findIndex((s) => s.id === id);
}

export function sceneById(id) {
  return SCENES.find((s) => s.id === id) ?? SCENES[0];
}
