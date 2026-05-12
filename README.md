# SIOP activity scoring: deterministic second rater

This repository is a **small research tool** that scores written lesson activities
against the **Sheltered Instruction Observation Protocol (SIOP)**—a widely used
framework for making grade-level content accessible to multilingual learners
while building academic language. From here on we refer to it as **SIOP**.

You paste or upload **plain-language descriptions of activities** (for example,
full lesson write-ups your team already has as text or spreadsheets). The tool
applies a transparent, rule-based “codebook” of indicators and produces a
**0–4 rating for each of 30 SIOP features** for every activity. If you also have
**human SIOP ratings** for the same activities, the app compares the two and
reports agreement statistics (for example Gwet’s AC2, Krippendorff’s α, weighted
Cohen’s κ) and a **5×5 confusion matrix** per feature so you can see where the
automated rater matches or disagrees with people.

**What you get in practice**

- A **Streamlit web app** to upload data, explore scores, charts, and per-activity
  detail—best for most users.
- A **command-line workflow** to regenerate CSV outputs in batch (useful for
  papers or reproducible pipelines).

The scoring logic lives in `siop_pipeline/codebook.py` (keywords, patterns, and
feature rules). A fuller methodological write-up can live alongside your data in
`final_analysis_outputs/SIOP_Codebook_and_Python_Pipeline.md` if you maintain that
file in your fork or private materials.

---

## One-time setup

From your clone of this repository (adjust the path):

```bash
cd path/to/Activity-Assessment
python3 -m venv siop_pipeline/.venv
source siop_pipeline/.venv/bin/activate   # Windows: siop_pipeline\.venv\Scripts\activate
pip install -r siop_pipeline/requirements.txt
```

## Option A — Web app (recommended)

```bash
cd path/to/Activity-Assessment
source siop_pipeline/.venv/bin/activate
streamlit run siop_pipeline/app.py
```

The app opens at <http://localhost:8501>. In the sidebar you can:

- Choose a default activity-text file or **upload your own** (`.txt` using the
  `===== Activity N | Excel row M | characters X =====` header format, or
  `.xlsx`).
- Choose a default human-ratings CSV, **upload your own**, or skip for
  **score-only** mode.
- Toggle whether to include features that usually need live observation (#18
  wait time, #25 engagement).
- Clear the cache and re-score after you edit `codebook.py`.

**Main tabs**

1. **Overview** — Heatmap of algorithm scores and per-feature means; if humans
   are loaded, deltas between human and algorithm.
2. **Algorithm scores** — Full table, optional diagnostic columns showing which
   indicators fired, plus CSV download.
3. **Reliability** — Per-feature agreement metrics, charts, and a pick-one-feature
   confusion matrix (when human scores exist).
4. **Per-activity inspector** — One activity at a time: text, 30 scores, and
   diagnostics.
5. **About** — Short description of the workflow and how to iterate on rules.

## Option B — CLI

Run from the repository root with paths to **your** text file and output
locations (create `siop_pipeline/outputs/` first if needed):

```bash
cd path/to/Activity-Assessment
source siop_pipeline/.venv/bin/activate

# 1. Score every activity
python siop_pipeline/pipeline.py \
    --texts final_analysis_outputs/activity_texts.txt \
    --out   siop_pipeline/outputs/algo_scores.csv

# 2. Compare to human ratings (optional)
python siop_pipeline/reliability.py \
    --human final_analysis_outputs/human_siop_ratings.csv \
    --algo  siop_pipeline/outputs/algo_scores.csv \
    --report siop_pipeline/outputs/reliability_report.csv \
    --confusion-dir siop_pipeline/outputs/confusion
```

Flags include `--texts`, `--out`, `--long-out`, `--human`, `--algo`, `--report`,
`--confusion-dir`, and `--include-excluded`. If you omit paths, built-in defaults
may point at filenames under `final_analysis_outputs/`—check `pipeline.py` and
`reliability.py` for the exact default strings in your checkout.

Module-style invocation also works:

```bash
python -m siop_pipeline.pipeline
python -m siop_pipeline.reliability
```

## Option C — Streamlit Community Cloud

The package uses **flat sibling imports** inside `siop_pipeline/` (for example
`from codebook import …`), which matches how [Streamlit Community Cloud](https://share.streamlit.io)
often expects a single app folder. You can deploy by pointing Streamlit at
`siop_pipeline/app.py` (or by copying the contents of `siop_pipeline/` to the repo
root if you prefer a flat layout).

`app.py` looks for default data files in this order:

1. `siop_pipeline/final_analysis_outputs/<file>`
2. `final_analysis_outputs/<file>` (repository root)
3. Next to `app.py`

Committing small sample `.txt` / `.csv` files (or placing them next to the app)
makes the “use default file” option work without uploads.

## Repository layout

```
siop_pipeline/
├── app.py              Streamlit UI
├── codebook.py         30 SIOP feature scorers + helpers
├── data_loader.py      Parses activity text bundles and human-rating CSVs
├── pipeline.py         Batch scoring CLI → algo_scores.csv (+ long form)
├── reliability.py      Agreement metrics + per-feature confusion CSVs
├── report.py           Optional reporting helpers
├── requirements.txt
├── data/               Optional: drop extra inputs here
└── outputs/            Generated CSVs (algo scores, reliability, confusion/)
docs/                   Optional writing / analysis memos (not required to run the app)
```

## What the outputs contain

- `outputs/algo_scores.csv` — One row per activity; columns `F1`–`F30` and
  optional `F1_diag`–`F30_diag` (JSON-style indicator counts).
- `outputs/reliability_report.csv` — One row per feature: sample size, AC2 (with
  bootstrap CI where implemented), weighted κ, ordinal α, exact and within-1
  agreement, standardized mean difference. Features **#18** and **#25** are
  excluded by default because they normally require classroom observation.
- `outputs/confusion/F{n}_confusion.csv` — 5×5 matrix for feature *n* (rows =
  human rating, columns = algorithm).

## Improving the scores

Edit the dictionaries and rules beside each feature in `codebook.py`, then
re-run `pipeline.py` and, if you use human comparison, `reliability.py`. That
edit → score → evaluate loop is the main way to refine the deterministic rater.
