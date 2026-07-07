# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.9",
# ]
# ///

from __future__ import annotations

import csv
import io
import json
import math
import os
import subprocess
import textwrap
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

# Matplotlib's first import on macOS may spend minutes in
# `system_profiler -xml SPFontsDataType`. We only need bundled DejaVu fonts, so
# return an empty system-font plist for that specific probe.
_REAL_CHECK_OUTPUT = subprocess.check_output


def _fast_font_probe(args: object, *pargs: object, **kwargs: object) -> bytes:
    if args == ["system_profiler", "-xml", "SPFontsDataType"]:
        return (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
            b'"http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
            b'<plist version="1.0"><array><dict><key>_items</key><array/></dict></array></plist>'
        )
    return _REAL_CHECK_OUTPUT(args, *pargs, **kwargs)


subprocess.check_output = _fast_font_probe

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import NullFormatter

subprocess.check_output = _REAL_CHECK_OUTPUT


OUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "ine-price-changes-spain"
START_YEAR = 2002
END_YEAR = 2025
START_MONTH_PERIOD = "2002M01"
END_MONTH_PERIOD = "2025M12"


@dataclass(frozen=True)
class CpiSeries:
    label: str
    table_id: int
    category_column: str
    category: str
    source_level: str
    note: str = ""


CPI_SERIES = [
    CpiSeries(
        "Educación superior",
        79183,
        "Subgrupos ECOICOP ver.2",
        "10.4 Educación Superior",
        "Subgrupo",
    ),
    CpiSeries(
        "Alimentos y bebidas",
        76125,
        "Grupos ECOICOP ver.2",
        "01 Alimentos y bebidas no alcohólicas",
        "Grupo",
    ),
    CpiSeries(
        "Vivienda y suministros",
        76125,
        "Grupos ECOICOP ver.2",
        "04 Vivienda, agua, electricidad, gas y otros combustibles",
        "Grupo",
        "El IPC espanol no incluye vivienda en propiedad imputada.",
    ),
    CpiSeries(
        "Educación infantil",
        79184,
        "Subclases ECOICOP ver.2",
        "10.1.0.1 Educación Infantil",
        "Subclase",
    ),
    CpiSeries(
        "Servicios médicos amb.",
        79183,
        "Subgrupos ECOICOP ver.2",
        "06.2 Servicios de cuidados ambulatorios",
        "Subgrupo",
    ),
    CpiSeries(
        "Muebles y hogar",
        76125,
        "Grupos ECOICOP ver.2",
        "05 Muebles, artículos del hogar y artículos para el mantenimiento corriente del hogar",
        "Grupo",
    ),
    CpiSeries(
        "Libros",
        76127,
        "Clases  ECOICOP ver.2",
        "09.7.1 Libros",
        "Clase",
        "Proxy de libros de texto; la subclase libros educativos empieza en 2007.",
    ),
    CpiSeries(
        "Automóviles",
        76127,
        "Clases  ECOICOP ver.2",
        "07.1.1 Automóviles",
        "Clase",
        "Proxy de coche nuevo; automoviles nuevos solo esta disponible desde 2017.",
    ),
    CpiSeries(
        "Hospitalarios",
        79183,
        "Subgrupos ECOICOP ver.2",
        "06.3 Servicios de cuidados hospitalarios",
        "Subgrupo",
    ),
    CpiSeries(
        "Vestido y calzado",
        76125,
        "Grupos ECOICOP ver.2",
        "03 Vestido y calzado",
        "Grupo",
    ),
    CpiSeries(
        "Servicios móviles",
        79184,
        "Subclases ECOICOP ver.2",
        "08.3.2.0 Servicios de comunicación móvil",
        "Subclase",
        "Disponible desde 2017; porcentaje acumulado desde esa media anual.",
    ),
    CpiSeries(
        "Juguetes",
        76127,
        "Clases  ECOICOP ver.2",
        "09.2.1 Juegos, juguetes y artículos relacionados con las aficiones ",
        "Clase",
    ),
    CpiSeries(
        "Equipos audiovisuales",
        79184,
        "Subclases ECOICOP ver.2",
        "08.1.4.0 Equipo para la recepción, grabación y reproducción de sonido e imagen",
        "Subclase",
        "Proxy de TVs.",
    ),
    CpiSeries(
        "Equipos informáticos",
        76127,
        "Clases  ECOICOP ver.2",
        "08.1.3 Equipos de procesamiento de información",
        "Clase",
        "Proxy de software/equipo informatico.",
    ),
]

GENERAL_CPI = CpiSeries(
    "IPC general",
    76125,
    "Grupos ECOICOP ver.2",
    "Índice general",
    "General",
)


def ine_csv_url(table_id: int) -> str:
    return f"https://www.ine.es/jaxiT3/files/t/csv_bdsc/{table_id}.csv"


def read_ine_table(table_id: int) -> list[dict[str, str]]:
    with urllib.request.urlopen(ine_csv_url(table_id)) as response:
        text = response.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text), delimiter=";"))


def parse_spanish_float(raw: str) -> float | None:
    cleaned = raw.strip().strip('"')
    if not cleaned:
        return None
    return float(cleaned.replace(".", "").replace(",", "."))


def month_to_date(period: str) -> date:
    year, month = period.split("M")
    return date(int(year), int(month), 1)


def quarter_to_date(period: str) -> date:
    year, quarter = period.split("T")
    month = 1 + (int(quarter) - 1) * 3
    return date(int(year), month, 1)


def average_points_by_year(points: list[dict[str, object]]) -> list[dict[str, object]]:
    by_year: dict[int, list[dict[str, object]]] = {}
    for point in points:
        by_year.setdefault(point["date"].year, []).append(point)

    annual_points = []
    for year in sorted(by_year):
        year_points = by_year[year]
        first = year_points[0]
        values = [float(point["value"]) for point in year_points]
        annual_points.append(
            {
                "date": date(year, 1, 1),
                "period": str(year),
                "value": sum(values) / len(values),
                "series": first["series"],
                "source_table": first["source_table"],
                "source_level": first["source_level"],
                "ine_category": first["ine_category"],
                "note": first.get("note", ""),
                "observations": len(values),
            }
        )
    return annual_points


def load_cpi_series(defn: CpiSeries, cache: dict[int, list[dict[str, str]]]) -> list[dict[str, object]]:
    rows = cache.setdefault(defn.table_id, read_ine_table(defn.table_id))
    points = []
    for row in rows:
        period = row.get("Periodo", "")
        if period < START_MONTH_PERIOD or period > END_MONTH_PERIOD:
            continue
        if row.get(defn.category_column) != defn.category:
            continue
        if row.get("Tipo de dato") != "Índice":
            continue
        value = parse_spanish_float(row["Total"])
        if value is None:
            continue
        points.append(
            {
                "date": month_to_date(period),
                "period": period,
                "value": value,
                "series": defn.label,
                "source_table": defn.table_id,
                "source_level": defn.source_level,
                "ine_category": defn.category,
                "note": defn.note,
            }
        )
    points.sort(key=lambda item: item["date"])
    if not points:
        raise RuntimeError(f"No data found for {defn.label}: {defn.category}")
    annual_points = average_points_by_year(points)
    add_percent_change(annual_points)
    return annual_points


def load_wage_series(cache: dict[int, list[dict[str, str]]]) -> list[dict[str, object]]:
    table_id = 11222
    rows = cache.setdefault(table_id, read_ine_table(table_id))
    points = []
    for row in rows:
        period = row.get("Periodo", "")
        if period < "2002T1" or period > "2025T4":
            continue
        if row.get("Corrección de efectos") != "Datos ajustados de estacionalidad y calendario":
            continue
        if row.get("Componentes del coste") != "Coste salarial total por hora":
            continue
        if row.get("Tipo de dato") != "Euros":
            continue
        value = parse_spanish_float(row["Total"])
        if value is None:
            continue
        points.append(
            {
                "date": quarter_to_date(period),
                "period": period,
                "value": value,
                "series": "Coste salarial por hora",
                "source_table": table_id,
                "source_level": "ETCL",
                "ine_category": "Coste salarial total por hora, ajustado de estacionalidad y calendario",
                "note": "Serie trimestral agregada a media anual; porcentaje acumulado 2002-2025.",
            }
        )
    points.sort(key=lambda item: item["date"])
    if not points:
        raise RuntimeError("No wage data found")
    annual_points = average_points_by_year(points)
    add_percent_change(annual_points)
    return annual_points


def load_median_wage_series(cache: dict[int, list[dict[str, str]]]) -> list[dict[str, object]]:
    table_id = 28191
    rows = cache.setdefault(table_id, read_ine_table(table_id))
    points = []
    for row in rows:
        if row.get("Sexo") != "Ambos sexos":
            continue
        if row.get("Comunidades autónomas") != "Total Nacional":
            continue
        if row.get("Medidas y percentiles") != "Mediana":
            continue
        value = parse_spanish_float(row["Total"])
        if value is None:
            continue
        year = int(row["Periodo"])
        points.append(
            {
                "date": date(year, 1, 1),
                "period": str(year),
                "value": value,
                "series": "Salario mediano bruto anual",
                "source_table": table_id,
                "source_level": "EAES",
                "ine_category": "Ambos sexos, Total Nacional, Mediana",
                "note": "Salario mediano bruto anual; serie disponible 2008-2024.",
                "observations": "",
            }
        )
    points.sort(key=lambda item: item["date"])
    if not points:
        raise RuntimeError("No median wage data found")
    add_percent_change(points)
    return points


def add_percent_change(points: list[dict[str, object]]) -> None:
    base_value = float(points[0]["value"])
    for point in points:
        point["pct_change"] = (float(point["value"]) / base_value - 1.0) * 100.0
        point["base_period"] = points[0]["period"]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "series",
        "period",
        "date",
        "value",
        "pct_change",
        "base_period",
        "source_table",
        "source_level",
        "ine_category",
        "note",
        "observations",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_summary(path: Path, series_points: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows = []
    for label, points in series_points.items():
        first = points[0]
        last = points[-1]
        rows.append(
            {
                "series": label,
                "base_period": first["period"],
                "end_period": last["period"],
                "base_value": round(float(first["value"]), 3),
                "end_value": round(float(last["value"]), 3),
                "pct_change": round(float(last["pct_change"]), 1),
                "source_table": first["source_table"],
                "ine_category": first["ine_category"],
                "note": first.get("note", ""),
            }
        )
    rows.sort(key=lambda item: float(item["pct_change"]), reverse=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def label_positions(end_values: list[tuple[str, float]], min_gap: float = 8.0) -> dict[str, float]:
    ordered = sorted(end_values, key=lambda item: item[1], reverse=True)
    placed: list[tuple[str, float]] = []
    for label, desired in ordered:
        if placed:
            y = min(desired, placed[-1][1] - min_gap)
        else:
            y = desired
        placed.append((label, y))

    bottom_limit = -98.0
    if placed and placed[-1][1] < bottom_limit:
        shift = bottom_limit - placed[-1][1]
        placed = [(label, y + shift) for label, y in placed]

    return dict(placed)


def color_for(label: str, end_pct: float, overall_pct: float) -> str:
    if label == "Coste salarial por hora":
        return "#d7191c"
    if label in {"Equipos informáticos", "Equipos audiovisuales"}:
        return "#12315f"
    if end_pct < 0:
        return "#168dbb"
    if end_pct >= overall_pct:
        return "#d40000"
    if end_pct >= 45:
        return "#9a2a16"
    return "#0f3460"


def affordability_color(end_pct: float) -> str:
    return "#a94c36" if end_pct >= 0 else "#3f735c"


def log_label_positions(
    end_values: list[tuple[str, float]],
    min_gap: float = 0.065,
    bottom_ratio: float = 0.045,
) -> dict[str, float]:
    ordered = sorted(end_values, key=lambda item: item[1], reverse=True)
    placed: list[tuple[str, float]] = []
    for label, desired_pct in ordered:
        desired_log = math.log(max(0.04, 1.0 + desired_pct / 100.0))
        if placed:
            y_log = min(desired_log, placed[-1][1] - min_gap)
        else:
            y_log = desired_log
        placed.append((label, y_log))

    bottom_log = math.log(bottom_ratio)
    if placed and placed[-1][1] < bottom_log:
        shift = bottom_log - placed[-1][1]
        placed = [(label, y_log + shift) for label, y_log in placed]

    return {label: math.exp(y_log) for label, y_log in placed}


def build_affordability_series(
    series_points: dict[str, list[dict[str, object]]],
    denominator_points: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    wage_by_period = {point["period"]: point for point in denominator_points}
    affordability: dict[str, list[dict[str, object]]] = {}

    for label, points in series_points.items():
        if label in {"Coste salarial por hora", "IPC general"}:
            continue
        common_points = [point for point in points if str(point["period"]) in wage_by_period]
        if not common_points:
            continue
        base_period = str(common_points[0]["period"])
        wage_base = wage_by_period[base_period]
        price_base_value = float(common_points[0]["value"])
        wage_base_value = float(wage_base["value"])
        adjusted_points = []
        for point in common_points:
            wage_point = wage_by_period.get(str(point["period"]))
            if wage_point is None:
                continue
            price_ratio = float(point["value"]) / price_base_value
            wage_ratio = float(wage_point["value"]) / wage_base_value
            affordability_ratio = price_ratio / wage_ratio
            adjusted_points.append(
                {
                    "series": label,
                    "period": point["period"],
                    "date": point["date"],
                    "value": affordability_ratio,
                    "affordability_pct": (affordability_ratio - 1.0) * 100.0,
                    "price_value": point["value"],
                    "wage_value": wage_point["value"],
                    "price_pct_change": point["pct_change"],
                    "wage_pct_change": (wage_ratio - 1.0) * 100.0,
                    "base_period": base_period,
                    "denominator_series": wage_base["series"],
                    "denominator_source_table": wage_base["source_table"],
                    "source_table": point["source_table"],
                    "source_level": point["source_level"],
                    "ine_category": point["ine_category"],
                    "note": point.get("note", ""),
                    "observations": point.get("observations", ""),
                }
            )
        affordability[label] = adjusted_points
    return affordability


def write_affordability_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "series",
        "period",
        "date",
        "value",
        "affordability_pct",
        "price_value",
        "wage_value",
        "price_pct_change",
        "wage_pct_change",
        "base_period",
        "denominator_series",
        "denominator_source_table",
        "source_table",
        "source_level",
        "ine_category",
        "note",
        "observations",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_affordability_summary(
    path: Path,
    affordability_points: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    rows = []
    for label, points in affordability_points.items():
        first = points[0]
        last = points[-1]
        rows.append(
            {
                "series": label,
                "base_period": first["base_period"],
                "end_period": last["period"],
                "affordability_pct": round(float(last["affordability_pct"]), 1),
                "price_pct_change": round(float(last["price_pct_change"]), 1),
                "wage_pct_change": round(float(last["wage_pct_change"]), 1),
                "denominator_series": first["denominator_series"],
                "denominator_source_table": first["denominator_source_table"],
                "source_table": first["source_table"],
                "ine_category": first["ine_category"],
                "note": first.get("note", ""),
            }
        )
    rows.sort(key=lambda item: float(item["affordability_pct"]), reverse=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def plot_affordability_chart(
    affordability_points: dict[str, list[dict[str, object]]],
    summary_rows: list[dict[str, object]],
) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#bfb8a6",
            "xtick.color": "#777469",
            "ytick.color": "#777469",
        }
    )
    bg = "#f7f2e6"
    fig, ax = plt.subplots(figsize=(11.8, 14.6), dpi=180)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    min_year = min(int(points[0]["base_period"]) for points in affordability_points.values())
    max_year = max(point["date"].year for points in affordability_points.values() for point in points)
    x_start = date(min_year, 1, 1)
    x_label = date(2026, 2, 1)
    x_right = date(2031, 2, 1)

    end_lookup = {row["series"]: float(row["affordability_pct"]) for row in summary_rows}
    plot_order = list(affordability_points.keys())
    for label in plot_order:
        points = affordability_points[label]
        end_pct = end_lookup[label]
        ax.plot(
            [point["date"] for point in points],
            [point["value"] for point in points],
            color=affordability_color(end_pct),
            linewidth=2.2,
            alpha=0.97,
            solid_capstyle="round",
            zorder=3,
        )

    ax.set_yscale("log")
    ax.set_ylim(0.18, 1.60)
    ax.set_xlim(x_start, x_right)
    y_ticks = [0.20, 0.40, 0.60, 0.80, 1.0, 1.20, 1.50]
    y_labels = ["-80%", "-60%", "-40%", "-20%", "0%", "+20%", "+50%"]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=12)
    ax.yaxis.set_minor_formatter(NullFormatter())
    x_tick_years = [min_year, 2012, 2017, 2020, max_year]
    ax.set_xticks([date(year, 1, 1) for year in x_tick_years])
    ax.set_xticklabels([str(year) for year in x_tick_years], fontsize=13)
    ax.tick_params(axis="x", length=7, width=1.0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", color="#d9d2c0", linewidth=0.9, zorder=0)

    ax.axhline(1.0, color="#1f252b", linewidth=3.0, zorder=5)
    ax.text(
        date(2017, 6, 1),
        1.015,
        "Salario mediano bruto anual",
        color="#1f252b",
        fontsize=9.7,
        fontweight="bold",
        ha="left",
        va="bottom",
        zorder=6,
    )
    ax.scatter([date(2025, 1, 1)], [1.0], s=38, facecolor=bg, edgecolor="#1f252b", linewidth=2, zorder=6)

    ax.axvline(date(2020, 1, 1), color="#c7c0ae", linewidth=0.9, zorder=1)
    ax.text(date(2020, 3, 1), 1.48, "Pandemia", color="#8b877b", fontsize=9.5, ha="left")

    label_y = log_label_positions(
        [(label, float(points[-1]["affordability_pct"])) for label, points in affordability_points.items()],
        min_gap=0.082,
        bottom_ratio=0.205,
    )
    for label in plot_order:
        points = affordability_points[label]
        end_pct = float(points[-1]["affordability_pct"])
        color = affordability_color(end_pct)
        y_text = label_y[label]
        end_ratio = float(points[-1]["value"])
        end_date = points[-1]["date"]
        ax.plot([end_date, x_label], [end_ratio, y_text], color=color, linewidth=0.8, alpha=0.55, zorder=2)
        ax.scatter([end_date], [end_ratio], s=30, facecolor=bg, edgecolor=color, linewidth=1.5, zorder=4)
        suffix = ""
        if int(points[0]["base_period"]) > min_year:
            suffix = f", desde {points[0]['base_period']}"
        ax.text(
            x_label,
            y_text,
            f"{label} ({end_pct:+.1f}%{suffix})",
            color=color,
            fontsize=10.6,
            fontweight="bold",
            ha="left",
            va="center",
            zorder=7,
        )

    ax.text(
        date(min_year, 9, 1),
        1.18,
        "MENOS ASEQUIBLE",
        color="#a94c36",
        fontsize=15,
        fontweight="bold",
        ha="left",
    )
    ax.text(
        date(min_year, 9, 1),
        0.225,
        "MÁS ASEQUIBLE",
        color="#3f735c",
        fontsize=15,
        fontweight="bold",
        ha="left",
    )

    fig.text(
        0.105,
        0.962,
        "¿SE HA ROTO EL SUEÑO ESPAÑOL?",
        fontsize=24,
        fontweight="bold",
        color="#1f252b",
        ha="left",
    )
    fig.text(
        0.105,
        0.938,
        "Precios seleccionados del IPC ajustados por salario mediano bruto anual. Medias anuales 2008-2024 (escala log).",
        fontsize=12.5,
        color="#777469",
        fontstyle="italic",
        ha="left",
    )

    footnote = (
        "Fuente: INE, IPC base 2025 (tablas 76125, 79183, 76127, 79184) y EAES "
        "(tabla 28191). Cada linea muestra precio/salario mediano bruto anual, rebased a la primera "
        "media anual disponible de la serie; por encima de 0% exige mas salario mediano que en la base. "
        "Repo: github.com/victoriano/ine-spain-price-changes."
    )
    fig.text(0.07, 0.053, textwrap.fill(footnote, 130), fontsize=8.4, color="#777469", ha="left")
    fig.text(
        0.77,
        0.037,
        "Producido por Victoriano Izquierdo",
        fontsize=10.5,
        fontweight="bold",
        color="#087fba",
        ha="left",
    )
    fig.text(0.77, 0.025, "@victorianoi en X", fontsize=9.5, color="#087fba", ha="left")

    fig.subplots_adjust(left=0.13, right=0.74, top=0.88, bottom=0.12)
    fig.savefig(OUT_DIR / "ine_spain_affordability_wages.png", bbox_inches="tight", facecolor=bg)
    fig.savefig(OUT_DIR / "ine_spain_affordability_wages.svg", bbox_inches="tight", facecolor=bg)
    plt.close(fig)


def plot_chart(series_points: dict[str, list[dict[str, object]]], summary_rows: list[dict[str, object]]) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#a3a3a3",
            "xtick.color": "#6f737a",
            "ytick.color": "#6f737a",
        }
    )
    fig, ax = plt.subplots(figsize=(10.8, 14.2), dpi=180)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    overall_pct = float(series_points["IPC general"][-1]["pct_change"])
    x_start = date(START_YEAR, 1, 1)
    x_label = date(2026, 6, 1)
    x_right = date(2030, 1, 1)

    end_lookup = {row["series"]: float(row["pct_change"]) for row in summary_rows}
    color_lookup = {label: color_for(label, pct, overall_pct) for label, pct in end_lookup.items()}

    plot_order = [
        label
        for label in series_points
        if label != "IPC general"
    ]
    for label in plot_order:
        points = series_points[label]
        color = color_lookup[label]
        ax.plot(
            [point["date"] for point in points],
            [point["pct_change"] for point in points],
            color=color,
            linewidth=3.2,
            solid_capstyle="round",
            alpha=0.98,
            zorder=3,
        )

    ax.axhline(0, color="#9a9a9a", linewidth=1.2, zorder=1)
    ax.axvline(date(2020, 1, 1), color="#b6b6b6", linewidth=0.9, zorder=1)
    ax.text(
        date(2020, 3, 1),
        128,
        "Pandemia",
        color="#8a8f98",
        fontsize=9.5,
        ha="left",
        va="center",
        zorder=2,
    )
    ax.grid(axis="y", color="#9c9c9c", linestyle=(0, (1.2, 2.4)), linewidth=0.75, zorder=0)
    ax.set_ylim(-105, 135)
    ax.set_xlim(x_start, x_right)
    ax.set_yticks([-100, -50, 0, 50, 100])
    ax.set_yticklabels([f"{tick}%" for tick in [-100, -50, 0, 50, 100]], fontsize=13)
    x_tick_years = [2002, 2007, 2012, 2017, 2020, 2025]
    ax.set_xticks([date(year, 1, 1) for year in x_tick_years])
    ax.set_xticklabels([str(year) for year in x_tick_years], fontsize=13)
    ax.tick_params(axis="x", length=7, width=1.0)
    ax.tick_params(axis="y", length=0)

    ax.hlines(overall_pct, x_start, date(2027, 1, 1), color="black", linewidth=5.8, zorder=6)
    ax.text(
        date(2002, 8, 1),
        overall_pct + 2.2,
        f"IPC general (+{overall_pct:.1f}%)",
        color="white",
        fontsize=12.2,
        fontweight="bold",
        va="center",
        ha="left",
        bbox=dict(facecolor="black", edgecolor="black", pad=6),
        zorder=7,
    )

    label_y = label_positions(
        [
            (label, float(points[-1]["pct_change"]))
            for label, points in series_points.items()
            if label != "IPC general"
        ],
        min_gap=7.6,
    )
    for label in plot_order:
        points = series_points[label]
        end_pct = float(points[-1]["pct_change"])
        color = color_lookup[label]
        y_text = label_y[label]
        end_date = points[-1]["date"]
        ax.plot([end_date, x_label], [end_pct, y_text], color=color, linewidth=1.2, alpha=0.6, zorder=2)
        suffix = ""
        if points[0]["period"] != str(START_YEAR) and label != "Coste salarial por hora":
            suffix = f", desde {points[0]['period']}"
        ax.text(
            x_label,
            y_text,
            f"{label} ({end_pct:+.1f}%{suffix})",
            color=color,
            fontsize=11.4,
            fontweight="bold",
            ha="left",
            va="center",
            zorder=8,
        )

    ax.text(
        date(2002, 10, 1),
        112,
        "MÁS\nCARO",
        color="#e00000",
        fontsize=15,
        fontweight="bold",
        ha="left",
        va="top",
    )
    ax.text(
        date(2002, 10, 1),
        -42,
        "MÁS\nASEQUIBLE",
        color="#1592c5",
        fontsize=15,
        fontweight="bold",
        ha="left",
        va="top",
    )

    fig.text(
        0.06,
        0.966,
        "Cambios de precios en España",
        fontsize=31,
        fontweight="bold",
        color="#282b31",
        ha="left",
    )
    fig.text(
        0.06,
        0.938,
        "(medias anuales, 2002-2025)",
        fontsize=24,
        fontweight="normal",
        color="#282b31",
        ha="left",
    )
    fig.text(
        0.06,
        0.910,
        "Bienes y servicios seleccionados del IPC del INE, y coste salarial por hora",
        fontsize=17,
        color="#282b31",
        ha="left",
    )

    footnote = (
        "Fuente: INE, IPC base 2025 (tablas 76125, 79183, 76127, 79184) y ETCL "
        "(tabla 11222). Cada punto es la media anual de la serie mensual o trimestral; "
        "variacion acumulada contra la primera media anual disponible. "
        "Repo: github.com/victoriano/ine-spain-price-changes."
    )
    fig.text(0.06, 0.042, textwrap.fill(footnote, 120), fontsize=8.8, color="#6f737a", ha="left")
    fig.text(
        0.77,
        0.038,
        "Producido por Victoriano Izquierdo",
        fontsize=11,
        fontweight="bold",
        color="#087fba",
        ha="left",
    )
    fig.text(0.77, 0.025, "@victorianoi en X", fontsize=10, color="#087fba", ha="left")

    # White band below the x-axis makes the source line feel separate from the plotting area.
    fig.patches.append(Rectangle((0, 0), 1, 0.02, transform=fig.transFigure, color="white", zorder=-1))

    fig.subplots_adjust(left=0.12, right=0.73, top=0.86, bottom=0.12)
    png_path = OUT_DIR / "ine_spain_price_changes.png"
    svg_path = OUT_DIR / "ine_spain_price_changes.svg"
    fig.savefig(png_path, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_methodology(path: Path, summary_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Cambios de precios en España con datos del INE",
        "",
        "Recreacion del grafico de cambios acumulados de precios, adaptada a Espana.",
        "",
        "## Criterio",
        "",
        "- Cada punto del grafico es una media anual.",
        "- Base principal: primera media anual disponible de cada serie dentro de 2002-2025.",
        "- La mayoria de partidas del IPC arrancan en 2002.",
        "- `Coste salarial por hora` es trimestral y se agrega a media anual para el grafico de cambios de precios.",
        "- `Salario mediano bruto anual` procede de la EAES y esta disponible para 2008-2024.",
        "- `Servicios moviles` empieza en 2017 en la subclase actual del INE.",
        "- La linea negra es el IPC general acumulado desde la media anual de 2002 hasta la media anual de 2025.",
        "- La linea vertical gris marca 2020 como referencia temporal de la pandemia.",
        "- Vivienda en IPC espanol no incluye vivienda en propiedad imputada; se usa el grupo de vivienda, agua, electricidad, gas y otros combustibles.",
        "- El grafico de asequibilidad divide cada serie de precios por el salario mediano bruto anual: `precio normalizado / salario mediano normalizado - 1`.",
        "- El grafico de asequibilidad no ajusta por impuestos; la mediana salarial de la EAES es bruta.",
        "",
        "## Fuentes",
        "",
        "- IPC grupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76125.csv",
        "- IPC subgrupos: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79183.csv",
        "- IPC clases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/76127.csv",
        "- IPC subclases: https://www.ine.es/jaxiT3/files/t/csv_bdsc/79184.csv",
        "- ETCL salarios por hora: https://www.ine.es/jaxiT3/files/t/csv_bdsc/11222.csv",
        "- EAES salario mediano bruto anual: https://www.ine.es/jaxiT3/files/t/csv_bdsc/28191.csv",
        "",
        "## Valores finales",
        "",
        "| Serie | Base | Fin | Cambio | Categoria INE | Nota |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in summary_rows:
        note = str(row.get("note", "")).replace("|", "/")
        lines.append(
            f"| {row['series']} | {row['base_period']} | {row['end_period']} | "
            f"{row['pct_change']:+.1f}% | {row['ine_category']} | {note} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache: dict[int, list[dict[str, str]]] = {}

    series_points: dict[str, list[dict[str, object]]] = {}
    series_points[GENERAL_CPI.label] = load_cpi_series(GENERAL_CPI, cache)
    for defn in CPI_SERIES:
        series_points[defn.label] = load_cpi_series(defn, cache)
    series_points["Coste salarial por hora"] = load_wage_series(cache)
    median_wage_points = load_median_wage_series(cache)

    all_rows = [point for points in series_points.values() for point in points]
    write_csv(OUT_DIR / "ine_spain_price_changes_series.csv", all_rows)
    write_csv(OUT_DIR / "ine_spain_median_wage_series.csv", median_wage_points)
    summary_rows = write_summary(OUT_DIR / "ine_spain_price_changes_summary.csv", series_points)
    plot_chart(series_points, summary_rows)
    write_methodology(OUT_DIR / "README.md", summary_rows)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    affordability_points = build_affordability_series(series_points, median_wage_points)
    affordability_rows = [point for points in affordability_points.values() for point in points]
    write_affordability_csv(OUT_DIR / "ine_spain_affordability_wages_series.csv", affordability_rows)
    affordability_summary_rows = write_affordability_summary(
        OUT_DIR / "ine_spain_affordability_wages_summary.csv",
        affordability_points,
    )
    plot_affordability_chart(affordability_points, affordability_summary_rows)
    (OUT_DIR / "affordability_summary.json").write_text(
        json.dumps(affordability_summary_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DIR / 'ine_spain_price_changes.png'}")
    print(f"Wrote {OUT_DIR / 'ine_spain_price_changes_series.csv'}")
    print(f"Wrote {OUT_DIR / 'ine_spain_price_changes_summary.csv'}")
    print(f"Wrote {OUT_DIR / 'ine_spain_median_wage_series.csv'}")
    print(f"Wrote {OUT_DIR / 'ine_spain_affordability_wages.png'}")
    print(f"Wrote {OUT_DIR / 'ine_spain_affordability_wages_series.csv'}")
    print(f"Wrote {OUT_DIR / 'ine_spain_affordability_wages_summary.csv'}")


if __name__ == "__main__":
    main()
