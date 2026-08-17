# Contributing (friends + upstream)

This repo is an **early shared toolkit**. Read `docs/FRIENDS_CANVAS.md` first.

## Model: one template, many personal copies

1. **Fork** (or keep your own private clone) for personal `config/`, `knowledge/evidence_bank.yaml`, `resumes/`, `data/`.
2. Add `upstream`:

```bash
git remote add upstream git@github.com:JunyiZhou-Conny/job-search-2026-2027-starter.git
git fetch upstream
git merge upstream/main   # or rebase — your choice
```

3. Improve the **shared engine** on a branch, then open a **Pull Request into this upstream repo**.
4. Everyone else pulls upstream to get your fix.

## Do contribute upstream
- `scripts/`, `static/`, `templates/`, `docs/`, tests
- Shared knowledge that isn’t identity-specific (`discovery_triage_rules.yaml`, `careers_boards.yaml`, `company_lists.yaml`)
- Experiment write-ups **without secrets**

## Don’t put in upstream PRs
- `secrets/`, cookies, storage_state
- Your filled `config/profile.yaml` / resumes / evidence bank
- Your `data/applications.csv` history (unless scrubbed examples)

## PR checklist
- [ ] No passwords, tokens, or session files
- [ ] Explains *what* and *why* in the PR body
- [ ] Prefer small diffs
- [ ] If you change discovery/queue behavior, note how to test it

## Questions
Open a GitHub Issue with label intent in the title, e.g. `friend-help: apply queue broken on …`.
