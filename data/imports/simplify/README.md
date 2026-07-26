# Simplify CSV imports

Drop nightly exports here as `YYYY-MM-DD.csv`, then:

```bash
python scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python scripts/jobsearch.py dashboard
```

Minimum useful columns: Company, Title, URL, Status, Date Applied.
