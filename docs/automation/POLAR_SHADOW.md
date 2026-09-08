# 48-hour Polar versus Cloud discovery shadow

Polar hourly discovery is the production candidate.
Cloud morning and evening discovery stays on. Do not disable the Automation on day one.

This file is the comparison checklist. It is not a preference.

## Window

Start when `discover-jobs-hourly` has actually run on the Mac.
End about 48 hours later. Use America/New_York days.

Keep both writers. Polar writes the Sheet. Cloud writes `generated/discovery_triage_*.csv` as it does today.

## What to count

For each 24-hour block, record:

| Metric | Polar | Cloud | Both |
|---|---|---|---|
| Unique jobs seen | | | |
| KEEP / READY rows | | | |
| SKIP rows | | | |
| Jobs only this side found | | | |
| Duplicate keys inside that side | | | |
| READY rows with a non-Jobright `apply_url` | | | |
| Hours from first listing sighting to queue or triage write | | | |

Use Jobright job id when both sides have it. Otherwise use normalized company + role + location.

## False KEEP and false SKIP

Do not score this from the agent that wrote the row.

Junyi or a later Cursor turn reviews a sample of 20 Polar READY rows and 20 Polar SKIP rows, plus every row only one side found.

A miss that Cloud found and Polar skipped needs a rule id. A Polar READY that violates `remote`, `non_us_location`, or `start_date_conflict` is a Polar false KEEP.

## What remains out of this comparison

Apply quality, writing quality, and Submit success are not discovery metrics.
Do not retire Cloud because Polar submitted a regular job.

## Evidence that lets us reduce Cloud

All of these must be true, with the table filled from real runs:

1. Polar hourly discovery ran unattended for two local days, including at least one locked-screen or backgrounded interval.
2. Polar found the Cloud KEEP rows that came from the same Jobright surfaces, or each Cloud-only KEEP has a written reason (login wall, board not in Polar's pass, Cloud Ashby sweep, scrape failure).
3. Polar-only READY rows were reviewed. False KEEP on hard rules is zero in that sample, or each miss has a compiler or prompt fix.
4. Polar duplicate rate by job_key is known and not worse than Cloud URL dedupe on the same days.
5. Original Job Post resolution was attempted on READY rows. Success and failure counts exist. Failures kept the Jobright URL.
6. The heartbeat tab shows the scheduler wrote at least one success while the Mac was unattended.

Then recommend one of:

- Keep Cloud as fallback at the current twice-daily cadence.
- Cut Cloud to one run per day.
- Retire Cloud discovery after one more week of Polar-only evidence.

Do not retire Cloud from preference. Do not retire it because Polar exists.

## What this does not prove

Locked-screen apply-ready-jobs.
Overnight regular Submit inside the canary caps.
Polar writing quality on prioritized rows.
Sheet writes during sleep, lid close, or Wi-Fi loss, unless those events happened in the window.
