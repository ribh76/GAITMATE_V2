from flask import Blueprint

from V1_reference.backend.services.csv_loader import (
    get_all_rows,
    get_latest_ligament_payload,
    get_latest_row,
    get_row_by_time,
)
from V1_reference.backend.utils.response_helpers import not_found, ok, server_error


sensor_bp = Blueprint("sensor", __name__)


@sensor_bp.get("/sensor/all")
def sensor_all():
    try:
        return ok({"rows": get_all_rows()})
    except Exception as exc:
        return server_error(str(exc))


@sensor_bp.get("/sensor/latest")
def sensor_latest():
    try:
        row = get_latest_row()
    except Exception as exc:
        return server_error(str(exc))
    if row is None:
        return not_found("No sensor rows found.")
    return ok(row)


@sensor_bp.get("/sensor/time/<time_value>")
def sensor_time(time_value):
    try:
        row = get_row_by_time(time_value)
    except Exception as exc:
        return server_error(str(exc))
    if row is None:
        return not_found(f"No sensor row found for time {time_value}.")
    return ok(row)


@sensor_bp.get("/sensor/ligaments/latest")
def sensor_ligaments_latest():
    try:
        payload = get_latest_ligament_payload()
    except Exception as exc:
        return server_error(str(exc))
    if payload is None:
        return not_found("No ligament data found.")
    return ok(payload)


@sensor_bp.get("/risk/latest")
def risk_latest():
    try:
        payload = get_latest_ligament_payload()
    except Exception as exc:
        return server_error(str(exc))
    if payload is None:
        return not_found("No risk data found.")
    return ok({"time": payload["time"], "overall": payload["overall"]})
