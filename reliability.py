"""Inter-rater reliability between human ratings and algorithm scores.

Reports per feature:
    * Gwet's AC2 (ordinal weights) with 95% CI
    * Krippendorff's α (ordinal)
    * Weighted Cohen's κ (quadratic)
    * Exact agreement %, within-1 agreement %
    * Standardized mean difference (algorithm − human)
Also writes a 5×5 confusion matrix per feature.

Usage::

    python -m siop_pipeline.reliability \
        --human final_analysis_outputs/siop_scoring_column_c_35_activities.csv \
        --algo  siop_pipeline/outputs/algo_scores.csv \
        --report siop_pipeline/outputs/reliability_report.csv \
        --confusion-dir siop_pipeline/outputs/confusion
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

import krippendorff

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from codebook import EXCLUDED_FEATURES, FEATURE_NAMES
from data_loader import load_human_scores


# ---------------------------------------------------------------------------
# Gwet's AC2 (ordinal, two raters)
# ---------------------------------------------------------------------------
# Formula (Gwet 2014, Handbook of Inter-Rater Reliability, 4th ed.):
#   AC2 = (P_a - P_e) / (1 - P_e)
#   P_a = Σ_kl w_kl * p_kl                 (weighted observed agreement)
#   P_e = (T_w / (q*(q-1))) * Σ_k π_k(1-π_k)
#   where T_w = Σ_{k≠l} w_kl  and  π_k = mean marginal proportion for category k.
# Ordinal (linear) weights used: w_kl = 1 - |k-l|/(q-1).

CATEGORIES = (0, 1, 2, 3, 4)


def _ordinal_weights(q: int) -> np.ndarray:
    idx = np.arange(q)
    return 1.0 - np.abs(idx[:, None] - idx[None, :]) / (q - 1)


def _gwet_ac2_point(
    h: np.ndarray, a: np.ndarray, q: int = 5
) -> float:
    n = len(h)
    if n == 0:
        return float("nan")
    p_kl = np.zeros((q, q))
    for hi, ai in zip(h, a):
        p_kl[int(hi), int(ai)] += 1
    p_kl /= n

    w = _ordinal_weights(q)
    p_a = float((w * p_kl).sum())

    pi = (p_kl.sum(axis=0) + p_kl.sum(axis=1)) / 2.0
    t_w = float(w.sum() - q)  # off-diagonal weight sum (diagonal w_kk=1)
    p_e = (t_w / (q * (q - 1))) * float((pi * (1 - pi)).sum())
    if p_e >= 1.0:
        return 1.0
    return (p_a - p_e) / (1 - p_e)


def gwet_ac2_ordinal(
    h: pd.Series, a: pd.Series, n_bootstrap: int = 2000, seed: int = 7
) -> tuple[float, str]:
    """Point estimate + 95% percentile-bootstrap CI string."""
    h_arr = h.values.astype(int)
    a_arr = a.values.astype(int)
    point = _gwet_ac2_point(h_arr, a_arr)
    n = len(h_arr)
    if n < 5:
        return point, "n<5"
    rng = np.random.default_rng(seed)
    boot = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        boot[b] = _gwet_ac2_point(h_arr[idx], a_arr[idx])
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    return point, f"[{lo:.3f}, {hi:.3f}]"


def _algo_wide(algo_csv: str | Path) -> pd.DataFrame:
    df = pd.read_csv(algo_csv)
    feat_cols = [c for c in df.columns if c.startswith("F") and "diag" not in c]
    out = df[["activity_id"] + feat_cols].copy()
    out = out.set_index("activity_id").sort_index()
    return out


def kappa_quadratic(h: pd.Series, a: pd.Series) -> float:
    return float(
        cohen_kappa_score(
            h.values, a.values, weights="quadratic", labels=[0, 1, 2, 3, 4]
        )
    )


def krip_ordinal(h: pd.Series, a: pd.Series) -> float:
    data = np.array([h.values, a.values], dtype=float)
    return float(
        krippendorff.alpha(
            reliability_data=data,
            level_of_measurement="ordinal",
            value_domain=[0, 1, 2, 3, 4],
        )
    )


def adjacent_agreement(h: pd.Series, a: pd.Series) -> dict[str, float]:
    diffs = np.abs(h.values - a.values)
    pooled_var = (h.var(ddof=1) + a.var(ddof=1)) / 2
    smd = (
        (a.mean() - h.mean()) / np.sqrt(pooled_var) if pooled_var > 0 else 0.0
    )
    return {
        "exact": float((diffs == 0).mean()),
        "within_1": float((diffs <= 1).mean()),
        "smd": float(smd),
    }


def per_feature_report(
    human: pd.DataFrame,
    algo: pd.DataFrame,
    exclude: tuple[int, ...] = EXCLUDED_FEATURES,
) -> pd.DataFrame:
    rows = []
    for col in sorted(
        set(human.columns) & set(algo.columns), key=lambda c: int(c[1:])
    ):
        fnum = int(col[1:])
        if fnum in exclude:
            continue
        h_full = human[col].dropna()
        a_full = algo[col].dropna()
        idx = h_full.index.intersection(a_full.index)
        h = h_full.loc[idx].astype(int)
        a = a_full.loc[idx].astype(int)
        if len(h) < 5:
            continue
        try:
            ac2, ci = gwet_ac2_ordinal(h, a)
        except Exception as e:
            ac2, ci = float("nan"), f"err: {e!r}"
        try:
            kappa = kappa_quadratic(h, a)
        except Exception:
            kappa = float("nan")
        try:
            alpha = krip_ordinal(h, a)
        except Exception:
            alpha = float("nan")
        adj = adjacent_agreement(h, a)
        rows.append(
            {
                "feature": col,
                "feature_name": FEATURE_NAMES.get(fnum, ""),
                "n": int(len(h)),
                "AC2_ordinal": round(ac2, 3),
                "AC2_CI": ci,
                "kappa_w": round(kappa, 3),
                "alpha_ordinal": round(alpha, 3),
                "exact_pct": round(adj["exact"] * 100, 1),
                "within_1_pct": round(adj["within_1"] * 100, 1),
                "SMD": round(adj["smd"], 3),
                "human_mean": round(float(h.mean()), 2),
                "algo_mean": round(float(a.mean()), 2),
            }
        )
    return pd.DataFrame(rows)


def confusion_per_feature(
    human: pd.DataFrame, algo: pd.DataFrame, output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for col in sorted(
        set(human.columns) & set(algo.columns), key=lambda c: int(c[1:])
    ):
        h_full = human[col].dropna()
        a_full = algo[col].dropna()
        idx = h_full.index.intersection(a_full.index)
        h = h_full.loc[idx].astype(int)
        a = a_full.loc[idx].astype(int)
        if len(h) == 0:
            continue
        cm = confusion_matrix(h, a, labels=[0, 1, 2, 3, 4])
        cm_df = pd.DataFrame(
            cm,
            index=[f"H={i}" for i in range(5)],
            columns=[f"A={i}" for i in range(5)],
        )
        cm_df.to_csv(output_dir / f"{col}_confusion.csv")


def pooled_summary(report: pd.DataFrame) -> pd.Series:
    """Single pooled-mean snapshot across all (non-excluded) features."""
    nums = ["AC2_ordinal", "kappa_w", "alpha_ordinal", "exact_pct", "within_1_pct"]
    return report[nums].mean().round(3)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute SIOP human-vs-algorithm reliability."
    )
    parser.add_argument(
        "--human",
        default="final_analysis_outputs/siop_scoring_column_c_35_activities.csv",
    )
    parser.add_argument(
        "--algo", default="siop_pipeline/outputs/algo_scores.csv"
    )
    parser.add_argument(
        "--report", default="siop_pipeline/outputs/reliability_report.csv"
    )
    parser.add_argument(
        "--confusion-dir", default="siop_pipeline/outputs/confusion"
    )
    parser.add_argument(
        "--include-excluded",
        action="store_true",
        help="Also report features #18 and #25 even though they're observation-dependent.",
    )
    args = parser.parse_args()

    human = load_human_scores(args.human)
    algo = _algo_wide(args.algo)

    print(f"Human ratings:    {human.shape[0]} activities × {human.shape[1]} features")
    print(f"Algorithm scores: {algo.shape[0]} activities × {algo.shape[1]} features")

    exclude = () if args.include_excluded else EXCLUDED_FEATURES
    report = per_feature_report(human, algo, exclude=exclude)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(report_path, index=False)

    confusion_per_feature(human, algo, Path(args.confusion_dir))

    print(f"\nPer-feature reliability written to {report_path}")
    print(f"Per-feature confusion matrices in {args.confusion_dir}/")
    print("\nPooled means (across reported features):")
    print(pooled_summary(report).to_string())
    print("\nFull report:")
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(report.to_string(index=False))


if __name__ == "__main__":
    main()
