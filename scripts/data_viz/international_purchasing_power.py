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
import re
import subprocess
import textwrap
import urllib.request
from dataclasses import dataclass
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
from matplotlib.ticker import FuncFormatter

subprocess.check_output = _REAL_CHECK_OUTPUT


OUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "international-purchasing-power"
WID_YEAR = 2024
INCOME_VARIABLE = "tdiincj992"
AVERAGE_VARIABLE = "adiincj992"
PPP_EUR_VARIABLE = "xlceupi999"
BIN_WIDTH_EUR = 5_000
PLOT_MAX_EUR = 130_000


@dataclass(frozen=True)
class Country:
    code: str
    label: str
    color: str
    linewidth: float = 2.4
    alpha: float = 0.96
    linestyle: str = "-"


COUNTRIES = [
    Country("ES", "España", "#4e5656", linewidth=2.9, alpha=0.92, linestyle=(0, (4, 3))),
    Country("FR", "Francia", "#b65442"),
    Country("GB", "Reino Unido", "#2f6690"),
    Country("CH", "Suiza", "#2d7b63"),
    Country("US", "EEUU", "#c7802f"),
]


def wid_csv_url(country_code: str) -> str:
    return f"https://wid.world/bulk_download/WID_data_{country_code}.csv"


def parse_percentile(raw: str) -> tuple[int, int] | None:
    match = re.fullmatch(r"p(\d+)p(\d+)", raw)
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    if end != start + 1:
        return None
    return start, end


def load_country(country: Country) -> dict[str, object]:
    thresholds: dict[int, float] = {}
    ppp_factor: float | None = None
    mean_local: float | None = None
    data_quality: str = ""

    with urllib.request.urlopen(wid_csv_url(country.code), timeout=90) as response:
        reader = csv.DictReader(io.TextIOWrapper(response, encoding="utf-8"), delimiter=";")
        for row in reader:
            if row["year"] != str(WID_YEAR):
                continue

            if row["variable"] == INCOME_VARIABLE:
                parsed = parse_percentile(row["percentile"])
                if parsed is None:
                    continue
                percentile, _ = parsed
                thresholds[percentile] = float(row["value"])
                data_quality = row.get("data_quality", data_quality)
                continue

            if row["variable"] == PPP_EUR_VARIABLE and row["percentile"] == "p0p100":
                ppp_factor = float(row["value"])
                continue

            if row["variable"] == AVERAGE_VARIABLE and row["percentile"] == "p0p100":
                mean_local = float(row["value"])

    missing = sorted(set(range(100)) - set(thresholds))
    if missing:
        raise RuntimeError(f"{country.code}: missing percentile thresholds for {missing[:8]}")
    if ppp_factor is None:
        raise RuntimeError(f"{country.code}: missing PPP EUR conversion factor")
    if mean_local is None:
        raise RuntimeError(f"{country.code}: missing average income")

    threshold_rows = []
    for percentile in sorted(thresholds):
        income_local = thresholds[percentile]
        income_eur_ppa = income_local / ppp_factor
        threshold_rows.append(
            {
                "country": country.label,
                "country_code": country.code,
                "year": WID_YEAR,
                "percentile": percentile,
                "adults_above_pct": 100 - percentile,
                "income_local": income_local,
                "ppp_eur_factor_lcu_per_eur": ppp_factor,
                "income_eur_ppa": income_eur_ppa,
                "data_quality": data_quality,
            }
        )

    thresholds_eur = {row["percentile"]: row["income_eur_ppa"] for row in threshold_rows}
    return {
        "country": country,
        "threshold_rows": threshold_rows,
        "thresholds_eur": thresholds_eur,
        "median_eur_ppa": thresholds_eur[50],
        "mean_eur_ppa": mean_local / ppp_factor,
        "p10_eur_ppa": thresholds_eur[10],
        "p90_eur_ppa": thresholds_eur[90],
        "ppp_factor": ppp_factor,
        "data_quality": data_quality,
    }


def pct_above_threshold(thresholds_eur: dict[int, float], reference: float) -> float:
    pairs = sorted((percentile, value) for percentile, value in thresholds_eur.items())
    if reference <= pairs[0][1]:
        return 100.0
    if reference >= pairs[-1][1]:
        return 1.0

    for (p0, v0), (p1, v1) in zip(pairs, pairs[1:]):
        if v0 <= reference <= v1:
            if math.isclose(v0, v1):
                percentile = p0
            else:
                percentile = p0 + ((reference - v0) / (v1 - v0)) * (p1 - p0)
            return 100.0 - percentile

    raise RuntimeError("Reference threshold could not be interpolated")


def cdf_percent(thresholds_eur: dict[int, float], value: float) -> float:
    pairs = sorted((percentile, income) for percentile, income in thresholds_eur.items() if percentile <= 99)
    if value <= pairs[0][1]:
        return 0.0
    if value >= pairs[-1][1]:
        return 99.0

    for (p0, v0), (p1, v1) in zip(pairs, pairs[1:]):
        if v0 <= value <= v1:
            if math.isclose(v0, v1):
                return float(p1)
            return p0 + ((value - v0) / (v1 - v0)) * (p1 - p0)

    return 99.0


def smooth_series(values: list[float]) -> list[float]:
    smoothed = []
    for index, value in enumerate(values):
        prev_value = values[index - 1] if index > 0 else value
        next_value = values[index + 1] if index < len(values) - 1 else value
        smoothed.append(prev_value * 0.25 + value * 0.5 + next_value * 0.25)
    return smoothed


def build_distribution_rows(country_data: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    bin_edges = list(range(0, PLOT_MAX_EUR + BIN_WIDTH_EUR, BIN_WIDTH_EUR))
    for item in country_data:
        country: Country = item["country"]
        thresholds_eur: dict[int, float] = item["thresholds_eur"]
        raw_values = []
        bin_specs = []
        for start, end in zip(bin_edges, bin_edges[1:]):
            share = max(0.0, cdf_percent(thresholds_eur, end) - cdf_percent(thresholds_eur, start))
            raw_values.append(share)
            bin_specs.append((start, end, (start + end) / 2))

        smoothed_values = smooth_series(raw_values)
        for (start, end, midpoint), raw_share, smoothed_share in zip(bin_specs, raw_values, smoothed_values):
            rows.append(
                {
                    "country": country.label,
                    "country_code": country.code,
                    "year": WID_YEAR,
                    "bin_start_eur_ppa": start,
                    "bin_end_eur_ppa": end,
                    "bin_midpoint_eur_ppa": midpoint,
                    "adults_pct_raw": round(raw_share, 4),
                    "adults_pct_smoothed": round(smoothed_share, 4),
                    "bin_width_eur_ppa": BIN_WIDTH_EUR,
                    "note": "Estimated from WID percentile thresholds; top 1 percent is open-ended and not fully shown.",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_eur_thousands(value: float) -> str:
    return f"{value / 1000:.0f}k"


def fmt_spanish_integer(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def build_summary(country_data: list[dict[str, object]]) -> list[dict[str, object]]:
    spain_median = next(item["median_eur_ppa"] for item in country_data if item["country"].code == "ES")
    summary = []
    for item in country_data:
        country = item["country"]
        percent_above_spain = pct_above_threshold(item["thresholds_eur"], float(spain_median))
        summary.append(
            {
                "country": country.label,
                "country_code": country.code,
                "year": WID_YEAR,
                "median_eur_ppa": round(float(item["median_eur_ppa"]), 1),
                "mean_eur_ppa": round(float(item["mean_eur_ppa"]), 1),
                "p10_eur_ppa": round(float(item["p10_eur_ppa"]), 1),
                "p90_eur_ppa": round(float(item["p90_eur_ppa"]), 1),
                "pct_above_spain_median": round(percent_above_spain, 1),
                "spain_median_reference_eur_ppa": round(float(spain_median), 1),
                "ppp_eur_factor_lcu_per_eur": round(float(item["ppp_factor"]), 6),
                "data_quality": item["data_quality"],
            }
        )
    summary.sort(key=lambda row: row["pct_above_spain_median"], reverse=True)
    return summary


def plot_chart(
    country_data: list[dict[str, object]],
    summary: list[dict[str, object]],
    distribution_rows: list[dict[str, object]],
) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": "#c9c2b0",
            "xtick.color": "#706d64",
            "ytick.color": "#706d64",
        }
    )
    bg = "#f7f2e6"
    text = "#1f252b"
    grid = "#ddd5c2"
    fig = plt.figure(figsize=(15.8, 9.2), dpi=180, facecolor=bg)
    gs = fig.add_gridspec(1, 2, width_ratios=[2.6, 1.1], wspace=0.22)
    ax = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])
    ax.set_facecolor(bg)
    ax_bar.set_facecolor(bg)

    spain_median = next(item["median_eur_ppa"] for item in country_data if item["country"].code == "ES")

    distribution_by_country: dict[str, list[dict[str, object]]] = {}
    for row in distribution_rows:
        distribution_by_country.setdefault(str(row["country_code"]), []).append(row)

    for item in country_data:
        country: Country = item["country"]
        rows = distribution_by_country[country.code]
        x = [float(row["bin_midpoint_eur_ppa"]) / 1000 for row in rows]
        y = [float(row["adults_pct_smoothed"]) for row in rows]
        ax.plot(
            x,
            y,
            color=country.color,
            linewidth=country.linewidth,
            alpha=country.alpha,
            linestyle=country.linestyle,
            solid_capstyle="round",
            label=country.label,
            zorder=4 if country.code != "ES" else 3,
        )

    ax.axvline(spain_median / 1000, color="#1f252b", linewidth=1.2, alpha=0.78, zorder=2)
    ax.text(
        spain_median / 1000 + 1.4,
        6.0,
        f"Mediana España: {fmt_eur_thousands(float(spain_median))} €-PPA",
        color=text,
        fontsize=9.8,
        fontweight="bold",
        ha="left",
        va="center",
    )
    ax.set_xlim(0, PLOT_MAX_EUR / 1000)
    ax.set_ylim(0, 16)
    ax.set_xlabel("Renta anual equivalente, miles de euros-PPA", fontsize=10.5, color=text, labelpad=10)
    ax.set_ylabel("% de adultos en cada tramo de 5.000 €-PPA", fontsize=10.5, color=text, labelpad=10)
    ax.set_xticks([0, 20, 40, 60, 80, 100, 120])
    ax.set_yticks([0, 4, 8, 12, 16])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{value:.0f}%"))
    ax.grid(axis="both", color=grid, linewidth=0.8, alpha=0.85, zorder=0)
    ax.legend(
        loc="upper right",
        frameon=False,
        fontsize=10.5,
        labelcolor=text,
        handlelength=2.4,
        borderaxespad=0.4,
    )

    ax.text(
        2,
        1.0,
        "Curvas aproximadas con umbrales percentilares WID\nNo es salario bruto ni microdato individual",
        fontsize=9.2,
        color="#777469",
        ha="left",
        va="bottom",
    )

    ordered = [row for row in summary if row["country_code"] != "ES"]
    ordered.append(next(row for row in summary if row["country_code"] == "ES"))
    color_by_code = {country.code: country.color for country in COUNTRIES}
    labels = [row["country"] for row in ordered]
    values = [float(row["pct_above_spain_median"]) for row in ordered]
    colors = [color_by_code[row["country_code"]] for row in ordered]
    y_pos = list(range(len(labels)))

    ax_bar.barh(y_pos, values, color=colors, height=0.56, alpha=0.92)
    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(labels, fontsize=10.5, color=text)
    ax_bar.invert_yaxis()
    ax_bar.set_xlim(0, 100)
    ax_bar.set_xticks([0, 25, 50, 75, 100])
    ax_bar.xaxis.set_major_formatter(FuncFormatter(lambda value, _pos: f"{value:.0f}%"))
    ax_bar.grid(axis="x", color=grid, linewidth=0.8, alpha=0.9, zorder=0)
    ax_bar.set_axisbelow(True)
    ax_bar.set_title(
        "% por encima de la\nmediana española",
        fontsize=12.5,
        color=text,
        fontweight="bold",
        loc="left",
        pad=12,
    )
    for idx, value in enumerate(values):
        ax_bar.text(
            min(value + 2, 96),
            idx,
            f"{value:.1f}%",
            va="center",
            ha="left" if value < 92 else "right",
            fontsize=10.4,
            color=text,
            fontweight="bold",
        )

    for spine in ["left", "bottom"]:
        ax_bar.spines[spine].set_color("#c9c2b0")
    ax_bar.tick_params(axis="y", length=0)
    ax_bar.tick_params(axis="x", length=0)

    fig.text(
        0.055,
        0.955,
        "PODER ADQUISITIVO COMPARADO",
        fontsize=26,
        fontweight="bold",
        color=text,
        ha="left",
    )
    fig.text(
        0.055,
        0.917,
        "Distribución aproximada por tramos de 5.000 €-PPA. Renta post-impuestos nacional por adulto equivalente. Adultos, 2024.",
        fontsize=13.2,
        color="#777469",
        fontstyle="italic",
        ha="left",
    )

    footnote = (
        "Fuente: WID.world, descargas bulk por país (ES, FR, GB, CH, US). Variable principal: tdiincj992 "
        "(umbrales de renta nacional post-impuestos, equal-split adults); conversión: xlceupi999 "
        "(moneda local por euro-PPA). Incluye redistribución en especie/gasto público imputado, por lo que "
        "no equivale a salario bruto ni a renta disponible estricta de caja. La curva principal estima una "
        "distribución por tramos desde umbrales percentilares; el top 1% es abierto. Repo: "
        "github.com/victoriano/ine-spain-price-changes."
    )
    fig.text(0.055, 0.047, textwrap.fill(footnote, 165), fontsize=8.2, color="#777469", ha="left")
    fig.text(
        0.735,
        0.047,
        "Producido por Victoriano Izquierdo",
        fontsize=10.2,
        fontweight="bold",
        color="#087fba",
        ha="left",
    )
    fig.text(0.735, 0.03, "@victorianoi en X", fontsize=9.3, color="#087fba", ha="left")

    fig.subplots_adjust(left=0.07, right=0.96, top=0.86, bottom=0.20)
    fig.savefig(OUT_DIR / "international_purchasing_power.png", bbox_inches="tight", facecolor=bg)
    fig.savefig(OUT_DIR / "international_purchasing_power.svg", bbox_inches="tight", facecolor=bg)
    plt.close(fig)


def write_readme(summary: list[dict[str, object]]) -> None:
    rows = "\n".join(
        "| {country} | {median:,.0f} | {mean:,.0f} | {above:.1f}% |".format(
            country=row["country"],
            median=row["median_eur_ppa"],
            mean=row["mean_eur_ppa"],
            above=row["pct_above_spain_median"],
        ).replace(",", ".")
        for row in summary
    )
    readme = f"""# Poder adquisitivo internacional

Comparación de España, Francia, Reino Unido, Suiza y EEUU con datos de WID.world. La renta se convierte a euros ajustados por paridad de poder adquisitivo (euros-PPA), no por tipo de cambio de mercado.

![Poder adquisitivo comparado](international_purchasing_power.png)

## Resumen

Referencia: mediana española de `{WID_YEAR}`, `{fmt_spanish_integer(next(row['spain_median_reference_eur_ppa'] for row in summary))}` euros-PPA por adulto equivalente.

| País | Mediana €-PPA | Media €-PPA | % por encima de la mediana española |
| --- | ---: | ---: | ---: |
{rows}

## Metodología

- Fuente: WID.world bulk downloads por país.
- Variable de renta: `tdiincj992`, umbral de renta nacional post-impuestos por percentil, adultos `equal-split`.
- Conversión a euros-PPA: cada umbral local se divide por `xlceupi999`, el factor de moneda local por euro-PPA.
- El panel principal aproxima una distribución: qué porcentaje de adultos cae en cada tramo de 5.000 euros-PPA. Se calcula interpolando los umbrales percentilares de WID, no con microdatos individuales.
- El panel derecho resume qué porcentaje de cada país supera la mediana española.

Esta no es una distribución de salario bruto. Es una métrica más amplia de nivel de vida porque incluye redistribución en especie/gasto público imputado dentro de la renta nacional post-impuestos. WID tiene también `cainc` para renta disponible post-impuestos estricta, pero en la descarga actual no ofrece umbrales/promedios con granularidad suficiente para construir este gráfico comparable.

## Archivos

- `international_purchasing_power.png`: gráfico final en PNG.
- `international_purchasing_power.svg`: versión vectorial.
- `international_purchasing_power_thresholds.csv`: umbrales por percentil, país y euros-PPA.
- `international_purchasing_power_distribution.csv`: distribución aproximada por tramos de 5.000 euros-PPA.
- `international_purchasing_power_summary.csv`: resumen por país.
- `summary.json`: resumen en JSON.
"""
    OUT_DIR.joinpath("README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    country_data = [load_country(country) for country in COUNTRIES]
    threshold_rows = [
        row
        for country_item in country_data
        for row in country_item["threshold_rows"]
    ]
    summary = build_summary(country_data)
    distribution_rows = build_distribution_rows(country_data)

    write_csv(OUT_DIR / "international_purchasing_power_thresholds.csv", threshold_rows)
    write_csv(OUT_DIR / "international_purchasing_power_distribution.csv", distribution_rows)
    write_csv(OUT_DIR / "international_purchasing_power_summary.csv", summary)
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(summary)
    plot_chart(country_data, summary, distribution_rows)


if __name__ == "__main__":
    main()
