"""Numbers and times the way a Vietnamese reader writes them.

Reasons, calculations and working papers printed Python's defaults: "1936.0 ≈
1936.0", "22,540,603 + 933,876", "8e+04", "09:30 UTC". A reviewer reads the
comma in 22,540,603 as a decimal point, and a judge spots each of these in the
first minute (TRANG_THAI_NOP_BAI §4). Every figure and time shown to a person
goes through here: 22.540.603, 12,5, 11/11/2026 09:30.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))


def number(value: float, decimals: int = 0) -> str:
    """Fixed decimals with Vietnamese separators: 22540603 → "22.540.603", (12.5, 1) → "12,5"."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def figure(value: float) -> str:
    """A quantity as reported, without float noise: 1936.0 → "1.936", 12.5 → "12,5", 0.35 → "0,35"."""
    if value != value:  # NaN
        return "?"
    if abs(value - round(value)) < 1e-9:
        return number(round(value), 0)
    magnitude = abs(value)
    decimals = 2 if magnitude >= 100 else 3 if magnitude >= 1 else 4
    text = number(value, decimals)
    return text.rstrip("0").rstrip(",") if "," in text else text


def signed(value: float) -> str:
    """A change with its sign: +12,5 / -3,2 / 0."""
    return f"+{figure(value)}" if value > 0 else figure(value)


# Canonical units (utils/text.py) as a reader writes them; tCO₂e is the recognised symbol.
_UNITS = {"tco2e": "tCO₂e", "tco2": "tCO₂", "kwh": "kWh", "mwh": "MWh", "gwh": "GWh", "m3": "m³",
          "tan": "tấn", "kg": "kg", "%": "%"}


def unit(name: str | None) -> str:
    """"tco2e" → "tCO₂e", "tan" → "tấn"; an unknown unit is returned as it is."""
    return _UNITS.get((name or "").lower(), name or "")


def vn_time(moment: datetime | str | None) -> str:
    """dd/mm/yyyy HH:MM in Vietnam time; a naive datetime or a bare ISO string is taken as UTC."""
    if not moment:
        return ""
    if isinstance(moment, str):
        try:
            moment = datetime.fromisoformat(moment.replace("Z", "+00:00"))
        except ValueError:
            return moment
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(VN_TZ).strftime("%d/%m/%Y %H:%M")
