# SIOP Deterministic Second-Rater Pipeline

A transparent, reproducible Python implementation of the 30-feature SIOP scoring
codebook described in `final_analysis_outputs/SIOP_Codebook_and_Python_Pipeline.md`,
with both a CLI and a Streamlit web app.

The pipeline reads each activity's Column-C text, applies feature-specific
indicator dictionaries, and emits a 0–4 score per (activity × feature). When
human ratings are available, it also reports inter-rater reliability (Gwet's
AC2 with ordinal weights and bootstrap CI, Krippendorff's α, weighted Cohen's
κ, exact / within-1 agreement, standardized mean difference) and a 5×5
confusion matrix per feature.

## One-time setup

```bash
cd /Users/farnaz/Desktop/gpt
python3 -m venv siop_pipeline/.venv
source siop_pipeline/.venv/bin/activate
pip install -r siop_pipeline/requirements.txt
```

## Option A — Web app (recommended)

```bash
cd /Users/farnaz/Desktop/gpt
source siop_pipeline/.venv/bin/activate
streamlit run siop_pipeline/app.py
```

The browser will open at <http://localhost:8501>. The sidebar lets you:

- pick the default activity-texts file or upload your own (`.txt` with the
  `===== Activity N | Excel row M | characters X =====` header format, or
  `.xlsx`);
- pick the default human-ratings CSV, upload your own, or skip entirely for
  score-only mode;
- toggle whether to include the excluded features (#18, #25);
- clear the cache and re-score any time you edit `codebook.py`.

The main area has five tabs:

1. **Overview** — algorithm score heatmap (35 × 30) and per-feature mean table
   with human-vs-algorithm deltas.
2. **Algorithm scores** — full wide-form table (with optional `_diag` columns
   exposing the indicator counts that drove each score) plus CSV download.
3. **Reliability** — per-feature AC2/κ/α/exact/within-1/SMD table, AC2 bar
   chart, signed disagreement heatmap (algorithm − human), and a confusion
   matrix for any single feature you pick.
4. **Per-activity inspector** — pick any activity, see the text side-by-side
   with the 30 algorithm scores (and human scores + Δ if available), plus the
   indicator diagnostics for every feature.
5. **About** — what the app does and the iteration loop.

## Option B — CLI

```bash
cd /Users/farnaz/Desktop/gpt
source siop_pipeline/.venv/bin/activate

# 1. score every activity
python -m siop_pipeline.pipeline

# 2. compare against your human ratings
python -m siop_pipeline.reliability
```

Both commands accept `--texts`, `--out`, `--human`, `--algo`, `--report`,
`--confusion-dir`, and `--include-excluded` flags. Defaults already point at
the files in `final_analysis_outputs/`.

## Layout

```
siop_pipeline/
├── app.py              Streamlit UI (option A above)
├── codebook.py         all 30 feature scorers + generic mapping helpers
├── data_loader.py      parses siop_column_c_full_text.txt and human-rating CSV
├── pipeline.py         score_all() + CLI; produces algo_scores.csv
├── reliability.py      Gwet's AC2 (in-house) / alpha / weighted kappa / confusion
├── requirements.txt
├── data/               drop additional inputs here if you want
└── outputs/            algo_scores.csv, reliability_report.csv, confusion/
```

## What each output contains

- `outputs/algo_scores.csv` — wide table, rows = activities (1..35), columns =
  `F1 … F30` plus `F1_diag … F30_diag` JSON blobs of indicator counts.
- `outputs/reliability_report.csv` — one row per feature with `n`, `AC2`,
  `AC2_CI`, `kappa_w`, `alpha_ord`, `exact_%`, `within_1_%`, `SMD`. Features
  #18 (wait time) and #25 (engagement) are excluded by default since they are
  observation-dependent.
- `outputs/confusion/F{n}_confusion.csv` — per-feature 5×5 confusion matrix
  (rows = human, cols = algorithm).

## Re-running with refined indicators

All regex/keyword dictionaries live in `codebook.py` next to their feature
function. Edit a dictionary, re-run `pipeline.py`, then re-run `reliability.py`
— this is the iteration loop the codebook describes in Part 5 step 7.
