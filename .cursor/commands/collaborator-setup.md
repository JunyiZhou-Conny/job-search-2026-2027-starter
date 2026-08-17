# /collaborator-setup

Set up a **personal fork** of this job-search toolkit for a friend / future collaborator.

This command is for the **collaborator’s** Cursor agent, not for rewriting Junyi’s identity on upstream `main`.

## Do this

1. Read and follow `docs/collaborators/SETUP.md` as the runbook.
2. Use the kickoff rules in `docs/collaborators/AGENT_KICKOFF.md`.
3. Ask Mode A / B / C if the human has not chosen.
4. For Mode A: prove `origin` is their fork, then run `scripts/init_personal_copy.py` (dry-run first).
5. Interview for facts. Write only confirmed facts. Use `unknown` otherwise.
6. Never submit applications, send outreach, or commit secrets.
7. End with `generated/collaborator_setup_status.md` plus one concrete next action.

## Do not

- Run `--write` when `origin` is `JunyiZhou-Conny/job-search-2026-2027-starter`
- Copy Junyi’s Simplify profile, applications, or resume bullets onto the collaborator
- Open an upstream PR that contains personal identity or ledger files
