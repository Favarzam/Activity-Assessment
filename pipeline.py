"""Score every activity against all 30 SIOP features and emit a CSV.

Run from the repo root (``/Users/farnaz/Desktop/gpt``)::

    python -m siop_pipeline.pipeline \
        --texts final_analysis_outputs/siop_column_c_full_text.txt \
        --out  siop_pipeline/outputs/algo_scores.csv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

# Allow `python pipeline.py …` to find sibling modules (Cloud-style flat layout)
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from codebook import FEATURE_NAMES, score_activity
from data_loader import load_activities


def score_all(activities: pd.DataFrame) -> pd.DataFrame:
    """Run all 30 scorers on every row of ``activities``.

    ``activities`` must contain ``activity_id`` and ``text`` columns.
    Returns a wide DataFrame with one row per activity.
    """
    rows: list[dict] = []
    for _, row in activities.iterrows():
        aid = int(row["activity_id"])
        text = row["text"] or ""
        scores, diags = score_activity(text)
        out: dict = {"activity_id": aid, "characters": len(text)}
        for fnum in sorted(scores):
            out[f"F{fnum}"] = scores[fnum]
        for fnum in sorted(diags):
            out[f"F{fnum}_diag"] = json.dumps(diags[fnum], default=str)
        rows.append(out)
    return pd.DataFrame(rows).sort_values("activity_id").reset_index(drop=True)


def write_long_form(scores_wide: pd.DataFrame, out_path: Path) -> None:
    """Also emit a long-form (activity_id, feature, score) table for plotting."""
    long_rows: list[dict] = []
    for _, row in scores_wide.iterrows():
        aid = int(row["activity_id"])
        for fnum, name in FEATURE_NAMES.items():
            col = f"F{fnum}"
            if col not in row:
                continue
            long_rows.append(
                {
                    "activity_id": aid,
                    "feature_num": fnum,
                    "feature_name": name,
                    "score_0_4": int(row[col]),
                }
            )
    pd.DataFrame(long_rows).to_csv(out_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score SIOP activities with the deterministic codebook."
    )
    parser.add_argument(
        "--texts",
        default="final_analysis_outputs/siop_column_c_full_text.txt",
        help="Path to the activity-texts file (.txt or .xlsx).",
    )
    parser.add_argument(
        "--out",
        default="siop_pipeline/outputs/algo_scores.csv",
        help="Where to write the wide-form algorithm scores CSV.",
    )
    parser.add_argument(
        "--long-out",
        default="siop_pipeline/outputs/algo_scores_long.csv",
        help="Where to write the long-form (activity, feature, score) CSV.",
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    long_path = Path(args.long_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    long_path.parent.mkdir(parents=True, exist_ok=True)

    activities = load_activities(args.texts)
    print(f"Loaded {len(activities)} activities from {args.texts}")

    scored = score_all(activities)
    scored.to_csv(out_path, index=False)
    write_long_form(scored, long_path)

    feature_cols = [c for c in scored.columns if c.startswith("F") and "diag" not in c]
    n_features = len(feature_cols)
    print(f"Scored {len(scored)} activities × {n_features} features")
    print(f"Wide-form scores → {out_path}")
    print(f"Long-form scores → {long_path}")

    summary = scored[feature_cols].mean().round(2).to_frame("mean_score")
    summary["feature_name"] = [
        FEATURE_NAMES.get(int(c[1:]), "") for c in summary.index
    ]
    print("\nMean score per feature (algorithm):")
    print(summary.to_string())


if __name__ == "__main__":
    main()
"""Score every activity against all 30 SIOP features and emit a CSV.

Run from the repo root (``/Users/farnaz/Desktop/gpt``)::

    python -m siop_pipeline.pipeline \
        --texts final_analysis_outputs/siop_column_c_full_text.txt \
        --out  siop_pipeline/outputs/algo_scores.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from siop_pipeline.codebook import FEATURE_NAMES, score_activity
from siop_pipeline.data_loader import load_activities


def score_all(activities: pd.DataFrame) -> pd.DataFrame:
    """Run all 30 scorers on every row of ``activities``.

    ``activities`` must contain ``activity_id`` and ``text`` columns.
    Returns a wide DataFrame with one row per activity.
    """
    rows: list[dict] = []
    for _, row in activities.iterrows():
        aid = int(row["activity_id"])
        text = row["text"] or ""
        scores, diags = score_activity(text)
        out: dict = {"activity_id": aid, "characters": len(text)}
        for fnum in sorted(scores):
            out[f"F{fnum}"] = scores[fnum]
        for fnum in sorted(diags):
            out[f"F{fnum}_diag"] = json.dumps(diags[fnum], default=str)
        rows.append(out)
    return pd.DataFrame(rows).sort_values("activity_id").reset_index(drop=True)


def write_long_form(scores_wide: pd.DataFrame, out_path: Path) -> None:
    """Also emit a long-form (activity_id, feature, score) table for plotting."""
    long_rows: list[dict] = []
    for _, row in scores_wide.iterrows():
        aid = int(row["activity_id"])
        for fnum, name in FEATURE_NAMES.items():
            col = f"F{fnum}"
            if col not in row:
                continue
            long_rows.append(
                {
                    "activity_id": aid,
                    "feature_num": fnum,
                    "feature_name": name,
                    "score_0_4": int(row[col]),
                }
            )
    pd.DataFrame(long_rows).to_csv(out_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score SIOP activities with the deterministic codebook."
    )
    parser.add_argument(
        "--texts",
        default="final_analysis_outputs/siop_column_c_full_text.txt",
        help="Path to the activity-texts file (.txt or .xlsx).",
    )
    parser.add_argument(
        "--out",
        default="siop_pipeline/outputs/algo_scores.csv",
        help="Where to write the wide-form algorithm scores CSV.",
    )
    parser.add_argument(
        "--long-out",
        default="siop_pipeline/outputs/algo_scores_long.csv",
        help="Where to write the long-form (activity, feature, score) CSV.",
    )
    args = parser.parse_args()

    out_path = Path(args.out)
    long_path = Path(args.long_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    long_path.parent.mkdir(parents=True, exist_ok=True)

    activities = load_activities(args.texts)
    print(f"Loaded {len(activities)} activities from {args.texts}")

    scored = score_all(activities)
    scored.to_csv(out_path, index=False)
    write_long_form(scored, long_path)

    feature_cols = [c for c in scored.columns if c.startswith("F") and "diag" not in c]
    n_features = len(feature_cols)
    print(f"Scored {len(scored)} activities × {n_features} features")
    print(f"Wide-form scores → {out_path}")
    print(f"Long-form scores → {long_path}")

    summary = scored[feature_cols].mean().round(2).to_frame("mean_score")
    summary["feature_name"] = [
        FEATURE_NAMES.get(int(c[1:]), "") for c in summary.index
    ]
    print("\nMean score per feature (algorithm):")
    print(summary.to_string())


if __name__ == "__main__":
    main()
