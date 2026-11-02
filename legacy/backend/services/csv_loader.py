from functools import lru_cache
from pathlib import Path

import pandas as pd

from V1_reference.backend.services.risk_engine import calculate_overall, calculate_risk


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "biosensor-data.csv"
LIGAMENTS = ("ATFL", "CFL", "PTFL")


def _clean_column_name(name):
    text = str(name).strip()
    return "metadata" if text.startswith("Unnamed") or text == "" else text


def _clean_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


@lru_cache(maxsize=1)
def _load_frame():
    df = pd.read_csv(DATA_FILE)
    df.columns = [_clean_column_name(column) for column in df.columns]
    return df


def _row_to_dict(row):
    return {key: _clean_value(value) for key, value in row.to_dict().items()}


def get_all_rows():
    return [_row_to_dict(row) for _, row in _load_frame().iterrows()]


def get_latest_row():
    df = _load_frame()
    if df.empty:
        return None
    return _row_to_dict(df.iloc[-1])


def get_row_by_time(time_value):
    df = _load_frame()
    matches = df[df["Time"].astype(str) == str(time_value)]
    if matches.empty:
        return None
    return _row_to_dict(matches.iloc[0])


sample_number = 0

def get_ligament_metrics(row):
    ligaments = {}
    for ligament in LIGAMENTS:
        average = row.get(f"{ligament} Average Strain",sample_number)
        max_strain = row.get(f"{ligament} Max Strain", sample_number)
        gradient = row.get(f"{ligament} Gradient", sample_number)
        variability = row.get(f"{ligament} Variability", sample_number)
        duration = row.get(f"{ligament} Duration", sample_number)
        loading = row.get(f"{ligament} Loading", sample_number)
        ligaments[ligament] = {
            "average_strain": average,
            "max_strain": max_strain,
            "gradient": gradient,
            "variability": variability,
            "duration": duration,
            "loading": loading,
            "risk": calculate_risk(max_strain, gradient, variability),
        }
    return ligaments


def get_latest_ligament_payload():
    row = get_latest_row()
    if row is None:
        return None
    ligaments = get_ligament_metrics(row)
    return {
        "time": row.get("Time"),
        "ligaments": ligaments,
        "overall": calculate_overall(ligaments, row.get("Overall")),
    }
