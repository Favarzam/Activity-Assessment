"""Streamlit UI for the SIOP deterministic second-rater pipeline.

Launch from the repo root::

    cd /Users/farnaz/Desktop/gpt
    source siop_pipeline/.venv/bin/activate
    streamlit run siop_pipeline/app.py

The browser will open at http://localhost:8501.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

# Make sibling .py files importable whether the app is launched as
#   `streamlit run siop_pipeline/app.py`  (local: app.py inside a package dir)
# or as Streamlit Cloud runs it
#   `streamlit run app.py`                (cloud: app.py at repo root with siblings)
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from codebook import (
    EXCLUDED_FEATURES,
    FEATURE_NAMES,
    score_activity,
)
from data_loader import (
    load_activities,
    load_activities_from_txt,
    load_activities_from_xlsx,
    load_human_scores,
)
from pipeline import score_all
from reliability import (
    per_feature_report,
    pooled_summary,
)


# Default data files. We look in three places (in order):
#   1. ./final_analysis_outputs/      (when app.py is at repo root, e.g. Cloud)
#   2. ../final_analysis_outputs/     (when app.py is inside siop_pipeline/)
#   3. ./                              (when the .txt / .csv sit next to app.py)
def _find_default(name: str) -> Path:
    for candidate in (
        _HERE / "final_analysis_outputs" / name,
        _HERE.parent / "final_analysis_outputs" / name,
        _HERE / name,
    ):
        if candidate.exists():
            return candidate
    return _HERE / "final_analysis_outputs" / name  # for the error message


DEFAULT_TEXTS = _find_default("siop_column_c_full_text.txt")
DEFAULT_HUMAN = _find_default("siop_scoring_column_c_35_activities.csv")
DATA_TMP_DIR = _HERE / "data"
DATA_TMP_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Page config + small CSS polish
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SIOP Deterministic Second-Rater",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 6px; }
        .stTabs [data-baseweb="tab"] {
            background: #f2f4f7; padding: 8px 16px; border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] { background: #1f6feb; color: white; }
        div[data-testid="stMetricValue"] { font-size: 1.6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Cached loaders + scorers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _activities_from_path(path: str) -> pd.DataFrame:
    return load_activities(path)


@st.cache_data(show_spinner=False)
def _activities_from_upload(name: str, payload: bytes) -> pd.DataFrame:
    suffix = Path(name).suffix.lower()
    tmp = DATA_TMP_DIR / f"_uploaded_texts{suffix}"
    tmp.write_bytes(payload)
    if suffix in (".xlsx", ".xls"):
        return load_activities_from_xlsx(tmp)
    return load_activities_from_txt(tmp)


@st.cache_data(show_spinner=False)
def _human_from_path(path: str) -> pd.DataFrame:
    return load_human_scores(path)


@st.cache_data(show_spinner=False)
def _human_from_upload(name: str, payload: bytes) -> pd.DataFrame:
    suffix = Path(name).suffix.lower()
    tmp = DATA_TMP_DIR / f"_uploaded_human{suffix}"
    tmp.write_bytes(payload)
    return load_human_scores(tmp)


@st.cache_data(show_spinner="Scoring activities…")
def _score_all_cached(_activities: pd.DataFrame, signature: tuple) -> pd.DataFrame:
    return score_all(_activities)


@st.cache_data(show_spinner="Computing reliability…")
def _reliability_cached(
    _human: pd.DataFrame,
    _algo_wide: pd.DataFrame,
    sig: tuple,
    include_excluded: bool,
) -> pd.DataFrame:
    exclude = () if include_excluded else EXCLUDED_FEATURES
    return per_feature_report(_human, _algo_wide, exclude=exclude)


def _algo_wide(scored: pd.DataFrame) -> pd.DataFrame:
    feat_cols = [c for c in scored.columns if c.startswith("F") and "diag" not in c]
    return scored.set_index("activity_id")[feat_cols].sort_index()


def _signature(df: pd.DataFrame) -> tuple:
    return (df.shape, int(pd.util.hash_pandas_object(df, index=True).sum()))


def _csv_bytes(df: pd.DataFrame, index: bool = False) -> bytes:
    return df.to_csv(index=index).encode("utf-8")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("📥 Inputs")

st.sidebar.markdown("**Activity texts**")
texts_choice = st.sidebar.radio(
    "Activity texts source",
    ["Use default", "Upload .txt or .xlsx"],
    label_visibility="collapsed",
)
texts_upload = None
if texts_choice.startswith("Upload"):
    texts_upload = st.sidebar.file_uploader(
        "Upload activity-texts file",
        type=["txt", "xlsx", "xls"],
        key="texts_upload",
    )
else:
    st.sidebar.caption(f"`{DEFAULT_TEXTS.name}`")

st.sidebar.markdown("---")

st.sidebar.markdown("**Human ratings (optional)**")
human_choice = st.sidebar.radio(
    "Human ratings source",
    ["Use default", "Upload .csv or .xlsx", "Skip — score-only"],
    label_visibility="collapsed",
)
human_upload = None
if human_choice.startswith("Upload"):
    human_upload = st.sidebar.file_uploader(
        "Upload human ratings file",
        type=["csv", "xlsx", "xls"],
        key="human_upload",
    )
elif human_choice.startswith("Use default"):
    st.sidebar.caption(f"`{DEFAULT_HUMAN.name}`")

st.sidebar.markdown("---")

include_excluded = st.sidebar.checkbox(
    "Include excluded features (#18, #25) in reliability report",
    value=False,
)

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Clear caches & re-score", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Codebook: `final_analysis_outputs/SIOP_Codebook_and_Python_Pipeline.md`"
)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("SIOP Deterministic Second-Rater")
st.caption(
    "Reproduces the 30-feature SIOP rubric on activity Column-C text via "
    "transparent regex/keyword indicators. Compares against human ratings "
    "using Gwet's AC2 (ordinal, bootstrap CI), Krippendorff's α, weighted κ, "
    "and exact / within-1 agreement."
)


# ---------------------------------------------------------------------------
# Load activity texts
# ---------------------------------------------------------------------------

activities: pd.DataFrame | None = None
try:
    if texts_choice.startswith("Use default"):
        if not DEFAULT_TEXTS.exists():
            st.error(f"Default texts file not found at {DEFAULT_TEXTS}")
        else:
            activities = _activities_from_path(str(DEFAULT_TEXTS))
    elif texts_upload is not None:
        activities = _activities_from_upload(
            texts_upload.name, texts_upload.getvalue()
        )
except Exception as e:
    st.error(f"Could not load activity texts: {e}")

if activities is None:
    st.info("👈 Pick an activity-texts source in the sidebar to begin.")
    st.stop()


# ---------------------------------------------------------------------------
# Score everything
# ---------------------------------------------------------------------------

scored = _score_all_cached(activities, _signature(activities))
algo_wide = _algo_wide(scored)
feature_cols = list(algo_wide.columns)


# ---------------------------------------------------------------------------
# Optional human ratings
# ---------------------------------------------------------------------------

human_wide: pd.DataFrame | None = None
human_err: str | None = None
if human_choice.startswith("Use default"):
    try:
        if DEFAULT_HUMAN.exists():
            human_wide = _human_from_path(str(DEFAULT_HUMAN))
        else:
            human_err = f"Default human ratings file not found at {DEFAULT_HUMAN}"
    except Exception as e:
        human_err = f"Could not load human ratings: {e}"
elif human_choice.startswith("Upload") and human_upload is not None:
    try:
        human_wide = _human_from_upload(
            human_upload.name, human_upload.getvalue()
        )
    except Exception as e:
        human_err = f"Could not load uploaded human ratings: {e}"

reliability_report: pd.DataFrame | None = None
if human_wide is not None:
    try:
        reliability_report = _reliability_cached(
            human_wide,
            algo_wide,
            (_signature(human_wide), _signature(algo_wide), include_excluded),
            include_excluded,
        )
    except Exception as e:
        human_err = f"Could not compute reliability: {e}"


# ---------------------------------------------------------------------------
# Top-line metrics
# ---------------------------------------------------------------------------

m1, m2, m3, m4 = st.columns(4)
m1.metric("Activities scored", f"{len(activities)}")
m2.metric("Features scored", f"{len(feature_cols)}")
m3.metric(
    "Cells produced",
    f"{len(activities) * len(feature_cols):,}",
)
if reliability_report is not None and not reliability_report.empty:
    pooled = pooled_summary(reliability_report)
    m4.metric(
        "Pooled AC2 (ordinal)",
        f"{pooled['AC2_ordinal']:.3f}",
        help="Mean Gwet's AC2 across all reported features.",
    )
elif human_err:
    m4.metric("Reliability", "—")
else:
    m4.metric("Reliability", "—", help="Provide human ratings to enable.")

if human_err:
    st.warning(human_err)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_overview, tab_scores, tab_reliability, tab_inspector, tab_about = st.tabs(
    [
        "🔭 Overview",
        "📊 Algorithm scores",
        "🤝 Reliability",
        "🔍 Per-activity inspector",
        "ℹ️ About",
    ]
)


# ---------------------------------------------------------------------------
# Overview tab
# ---------------------------------------------------------------------------

with tab_overview:
    st.subheader("Score heatmap (algorithm)")
    st.caption(
        "Rows = activities, columns = SIOP features (F1 … F30). "
        "Color = 0–4 score. Hover for the indicator name."
    )
    long = (
        algo_wide.reset_index()
        .melt(id_vars="activity_id", var_name="feature", value_name="score")
    )
    long["feature_num"] = long["feature"].str[1:].astype(int)
    long["feature_name"] = long["feature_num"].map(FEATURE_NAMES)
    chart = (
        alt.Chart(long)
        .mark_rect()
        .encode(
            x=alt.X(
                "feature:N",
                sort=[f"F{i}" for i in range(1, 31)],
                title="SIOP feature",
            ),
            y=alt.Y("activity_id:O", title="Activity"),
            color=alt.Color(
                "score:Q",
                scale=alt.Scale(scheme="viridis", domain=[0, 4]),
                legend=alt.Legend(title="Score 0–4"),
            ),
            tooltip=[
                "activity_id",
                "feature",
                alt.Tooltip("feature_name:N", title="Feature"),
                "score",
            ],
        )
        .properties(height=min(20 * len(activities), 700))
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Mean score per feature")
    means = (
        algo_wide.mean()
        .round(2)
        .to_frame("algorithm_mean")
        .assign(
            feature_name=lambda d: [FEATURE_NAMES[int(c[1:])] for c in d.index]
        )
    )
    if human_wide is not None:
        h_means = human_wide.mean().round(2).to_frame("human_mean")
        means = means.join(h_means, how="left")
        means["delta_algo_minus_human"] = (
            means["algorithm_mean"] - means["human_mean"]
        ).round(2)
    st.dataframe(means, use_container_width=True)


# ---------------------------------------------------------------------------
# Algorithm scores tab
# ---------------------------------------------------------------------------

with tab_scores:
    st.subheader("Wide-form scores (35 × 30)")
    st.caption(
        "Each cell is the deterministic 0–4 score. The right-hand `_diag` "
        "columns expose the indicator counts that drove each decision."
    )

    show_diag = st.toggle("Show diagnostic columns", value=False)
    cols_to_show = (
        list(scored.columns)
        if show_diag
        else [c for c in scored.columns if not c.endswith("_diag")]
    )
    st.dataframe(
        scored[cols_to_show], use_container_width=True, hide_index=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Download wide-form CSV",
            data=_csv_bytes(scored),
            file_name="algo_scores.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        long = (
            algo_wide.reset_index()
            .melt(id_vars="activity_id", var_name="feature", value_name="score_0_4")
        )
        long["feature_num"] = long["feature"].str[1:].astype(int)
        long["feature_name"] = long["feature_num"].map(FEATURE_NAMES)
        long = long[["activity_id", "feature_num", "feature_name", "score_0_4"]]
        st.download_button(
            "⬇️ Download long-form CSV",
            data=_csv_bytes(long),
            file_name="algo_scores_long.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Reliability tab
# ---------------------------------------------------------------------------

with tab_reliability:
    if reliability_report is None or reliability_report.empty:
        st.info(
            "Provide human ratings in the sidebar to enable the reliability "
            "comparison."
        )
    else:
        st.subheader("Per-feature reliability")
        st.caption(
            "AC2_ordinal = Gwet's AC2 with ordinal weights (95% CI from "
            "2,000 bootstrap resamples). kappa_w = quadratic weighted κ. "
            "alpha_ordinal = Krippendorff's α (ordinal). "
            "SMD = (algorithm − human) standardized mean difference."
        )
        st.dataframe(
            reliability_report, use_container_width=True, hide_index=True
        )

        st.markdown("**Pooled means across reported features**")
        pooled = pooled_summary(reliability_report)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("AC2 (ordinal)", f"{pooled['AC2_ordinal']:.3f}")
        c2.metric("Weighted κ", f"{pooled['kappa_w']:.3f}")
        c3.metric("Krippendorff α", f"{pooled['alpha_ordinal']:.3f}")
        c4.metric("Exact %", f"{pooled['exact_pct']:.1f}")
        c5.metric("Within-1 %", f"{pooled['within_1_pct']:.1f}")

        st.subheader("AC2 per feature")
        chart = (
            alt.Chart(reliability_report)
            .mark_bar()
            .encode(
                y=alt.Y("feature:N", sort="-x", title="Feature"),
                x=alt.X("AC2_ordinal:Q", title="Gwet's AC2 (ordinal)"),
                color=alt.Color(
                    "AC2_ordinal:Q",
                    scale=alt.Scale(
                        domain=[-0.2, 0.4, 0.6, 1.0],
                        range=["#d73a49", "#d73a49", "#f7b500", "#1f6feb"],
                    ),
                    legend=alt.Legend(title="AC2"),
                ),
                tooltip=[
                    "feature",
                    "feature_name",
                    "n",
                    "AC2_ordinal",
                    "AC2_CI",
                    "kappa_w",
                    "alpha_ordinal",
                    "exact_pct",
                    "within_1_pct",
                    "SMD",
                ],
            )
            .properties(height=20 * len(reliability_report) + 40)
        )
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Disagreement heatmap (algorithm − human)")
        common_idx = algo_wide.index.intersection(human_wide.index)
        common_cols = [c for c in algo_wide.columns if c in human_wide.columns]
        diff = (
            algo_wide.loc[common_idx, common_cols]
            - human_wide.loc[common_idx, common_cols]
        )
        long_diff = (
            diff.reset_index()
            .melt(id_vars="activity_id", var_name="feature", value_name="delta")
        )
        long_diff["feature_num"] = long_diff["feature"].str[1:].astype(int)
        long_diff["feature_name"] = long_diff["feature_num"].map(FEATURE_NAMES)
        diff_chart = (
            alt.Chart(long_diff)
            .mark_rect()
            .encode(
                x=alt.X(
                    "feature:N",
                    sort=[f"F{i}" for i in range(1, 31)],
                    title="SIOP feature",
                ),
                y=alt.Y("activity_id:O", title="Activity"),
                color=alt.Color(
                    "delta:Q",
                    scale=alt.Scale(scheme="redblue", domain=[-4, 4], reverse=True),
                    legend=alt.Legend(title="Algo − Human"),
                ),
                tooltip=[
                    "activity_id",
                    "feature",
                    "feature_name",
                    "delta",
                ],
            )
            .properties(height=min(20 * len(common_idx), 700))
        )
        st.altair_chart(diff_chart, use_container_width=True)

        st.subheader("Confusion matrix (single feature)")
        feature_pick = st.selectbox(
            "Feature to inspect",
            options=[
                f"F{n} — {FEATURE_NAMES[n]}"
                for n in sorted(int(c[1:]) for c in common_cols)
            ],
        )
        fnum = int(feature_pick.split(" — ")[0][1:])
        col = f"F{fnum}"
        h = human_wide[col].dropna().astype(int)
        a = algo_wide[col].dropna().astype(int)
        idx = h.index.intersection(a.index)
        h, a = h.loc[idx], a.loc[idx]
        cm = pd.crosstab(h, a, rownames=["Human"], colnames=["Algorithm"])
        for i in range(5):
            if i not in cm.index:
                cm.loc[i] = 0
            if i not in cm.columns:
                cm[i] = 0
        cm = cm.reindex(index=range(5), columns=range(5)).fillna(0).astype(int)
        st.dataframe(cm, use_container_width=True)

        st.download_button(
            "⬇️ Download reliability report CSV",
            data=_csv_bytes(reliability_report),
            file_name="reliability_report.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# Per-activity inspector tab
# ---------------------------------------------------------------------------

with tab_inspector:
    st.subheader("Drill into one activity")
    aid = st.selectbox(
        "Activity",
        options=activities["activity_id"].tolist(),
        format_func=lambda i: f"Activity {i} ({int(activities.set_index('activity_id').loc[i, 'characters'])} chars)",
    )

    text = activities.set_index("activity_id").loc[aid, "text"]
    scores, diags = score_activity(text)

    cL, cR = st.columns([1, 1])
    with cL:
        st.markdown("**Activity text**")
        st.text_area("Activity text", value=text, height=420, label_visibility="collapsed")

    with cR:
        st.markdown("**Algorithm scores**")
        rows = []
        for fnum in sorted(scores):
            row = {
                "Feature": f"F{fnum}",
                "Name": FEATURE_NAMES[fnum],
                "Algorithm": scores[fnum],
            }
            if human_wide is not None and aid in human_wide.index:
                hv = human_wide.loc[aid, f"F{fnum}"]
                row["Human"] = (
                    int(hv) if pd.notna(hv) else None
                )
                if pd.notna(hv):
                    row["Δ"] = int(scores[fnum] - hv)
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=420)

    st.markdown("**Indicator diagnostics**")
    st.caption(
        "Each row exposes the indicator counts that produced the score, so "
        "you can audit any disagreement."
    )
    diag_rows = []
    for fnum in sorted(diags):
        diag_rows.append(
            {
                "Feature": f"F{fnum}",
                "Name": FEATURE_NAMES[fnum],
                "Score": scores[fnum],
                "Diagnostics": json.dumps(diags[fnum], default=str),
            }
        )
    st.dataframe(pd.DataFrame(diag_rows), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# About tab
# ---------------------------------------------------------------------------

with tab_about:
    st.markdown(
        """
### What this app does

Implements the deterministic 30-feature SIOP codebook from
`final_analysis_outputs/SIOP_Codebook_and_Python_Pipeline.md` as a transparent
"second rater". For every activity Column-C text:

1. Each feature applies its own indicator dictionary (regex / keyword categories).
2. Indicators are mapped to a 0–4 score using the generic
   `hits / distinct / section_coverage / integration_marker` rubric, with
   per-feature overrides where the codebook specifies them.
3. Cross-feature cap rules tie F23 to F1, F24 to F2, and F27 to F9.
4. When human ratings are provided, per-feature reliability is reported
   (Gwet's AC2 ordinal with bootstrap CI, Krippendorff's α, weighted Cohen's κ,
   exact / within-1 agreement, standardized mean difference, plus a 5×5
   confusion matrix per feature).

### Inputs

- **Activity texts** — either the default
  `final_analysis_outputs/siop_column_c_full_text.txt` (with
  `===== Activity N | Excel row M | characters X =====` headers) or any
  `.xlsx` whose first column is `activity_id` and third column is the text.
- **Human ratings** *(optional)* — the default
  `siop_scoring_column_c_35_activities.csv`, or any long-form CSV/XLSX
  containing `Activity_ID`, `Feature_Num`, `Score_0_4` columns.

### Iteration loop

When a feature shows weak AC2 in the **Reliability** tab:

1. Open the **Per-activity inspector** and look at the 3–5 most divergent
   activities for that feature.
2. Edit the indicator dictionary for that feature in
   `siop_pipeline/codebook.py` (each `score_fN_*` function has its `cats =
   {…}` block at the top).
3. Click **🔄 Clear caches & re-score** in the sidebar.

Excluded by default: F18 (wait time, not recoverable from text) and F25
(engagement, observation-dependent). Tick the sidebar checkbox to include
them anyway.
        """
    )
