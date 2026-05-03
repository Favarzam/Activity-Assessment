"""Loaders for SIOP source texts and human ratings.

Two formats are supported for the activity texts:

1. ``siop_column_c_full_text.txt`` — the file already in
   ``final_analysis_outputs/``. Activities are delimited by
   ``===== Activity N | Excel row M | characters X =====``.
2. An ``.xlsx`` workbook whose first non-header column is the activity id and
   third column is the activity text (matches the layout described in the
   codebook's ``Part 4.4 pipeline.py`` example).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


_ACTIVITY_HEADER = re.compile(
    r"^=====\s*Activity\s+(\d+)\s*\|\s*Excel\s+row\s+(\d+)\s*\|\s*"
    r"characters\s+(\d+)\s*=====\s*$",
    re.MULTILINE,
)


def load_activities_from_txt(path: str | Path) -> pd.DataFrame:
    """Parse the ``siop_column_c_full_text.txt`` file into a DataFrame.

    Returns columns: activity_id (int), excel_row (int), text (str),
    characters (int).
    """
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    matches = list(_ACTIVITY_HEADER.finditer(raw))
    rows = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = raw[start:end].strip()
        rows.append(
            {
                "activity_id": int(m.group(1)),
                "excel_row": int(m.group(2)),
                "characters": int(m.group(3)),
                "text": body,
            }
        )
    if not rows:
        raise ValueError(
            f"No '===== Activity N | Excel row M | characters X =====' "
            f"headers found in {path}"
        )
    return pd.DataFrame(rows).sort_values("activity_id").reset_index(drop=True)


def load_activities_from_xlsx(
    path: str | Path,
    sheet: str | int = 0,
    id_col: int = 0,
    text_col: int = 2,
    skip_header: bool = True,
) -> pd.DataFrame:
    """Generic Excel loader. Defaults match the codebook's example layout."""
    df = pd.read_excel(path, sheet_name=sheet, header=0 if skip_header else None)
    rows = []
    for _, row in df.iterrows():
        aid = row.iloc[id_col]
        text = row.iloc[text_col]
        if pd.isna(aid) or pd.isna(text):
            continue
        rows.append(
            {
                "activity_id": int(aid),
                "excel_row": None,
                "characters": len(str(text)),
                "text": str(text),
            }
        )
    return pd.DataFrame(rows).sort_values("activity_id").reset_index(drop=True)


def load_activities(path: str | Path) -> pd.DataFrame:
    """Dispatch on file extension."""
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        return load_activities_from_xlsx(p)
    return load_activities_from_txt(p)


def load_human_scores(
    path: str | Path,
    activity_col: str = "Activity_ID",
    feature_col: str = "Feature_Num",
    score_col: str = "Score_0_4",
) -> pd.DataFrame:
    """Load the human ratings CSV/XLSX into a wide table.

    Returns a DataFrame indexed by ``activity_id`` with columns
    ``F1 .. F30`` (any missing features are NaN).
    """
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(p)
    else:
        df = pd.read_csv(p)
    pivot = df.pivot_table(
        index=activity_col,
        columns=feature_col,
        values=score_col,
        aggfunc="first",
    )
    pivot.columns = [f"F{int(c)}" for c in pivot.columns]
    pivot.index.name = "activity_id"
    return pivot.sort_index()
