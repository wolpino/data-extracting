# Testdata (fake only)

Buffy-themed fixtures for upload / extract demos. **Not real PHI.**

| File | First | Last | DOB (ISO) | Notes |
|------|-------|------|-----------|--------|
| [DME Patient Demo Document CPAP.fax.pdf](./DME%20Patient%20Demo%20Document%20CPAP.fax.pdf) | _(extract from PDF)_ | _(extract)_ | _(extract)_ | Assessment sample (~2MB fax-style) |
| [buffy-summers-chart.pdf](./buffy-summers-chart.pdf) | Buffy | Summers | 1981-01-19 | Small happy-path chart |
| [willow-rosenberg-chart.pdf](./willow-rosenberg-chart.pdf) | Willow | Rosenberg | 1981-05-01 | Second patient |
| [xander-harris-chart.pdf](./xander-harris-chart.pdf) | Alexander | Harris | 1981-03-15 | “Xander”; first name on PDF is Alexander |
| [spike-order-note.pdf](./spike-order-note.pdf) | William | Pratt | 1970-06-06 | Also known as Spike |

Regenerate small charts (from repo root):

```bash
python3 docs/testdata/generate_buffy_pdfs.py
```
