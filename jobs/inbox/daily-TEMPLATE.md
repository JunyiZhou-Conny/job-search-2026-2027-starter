# Daily inbox — YYYY-MM-DD

The "Daily Job Discovery" Cursor Automation writes this file automatically from the
intern and new-grad boards. You normally do not fill it in by hand.

What lands here:

- one line per merged unique role (company — role — url — source)
- the counts for that run
- anything the run could not fetch

Then work from the apply queue, not from this file:

```bash
python3 scripts/serve_apply_queue.py --date YYYY-MM-DD
```

If you want to add a role you found yourself, put it straight into the queue's day by
adding it to `data/applications.csv` via:

```bash
python3 scripts/jobsearch.py add-job --company "..." --role "..." --url "https://..."
```

Do **not** put passwords here.
