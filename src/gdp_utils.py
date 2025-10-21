# src/gdp_utils.py
from __future__ import annotations
from typing import List, Dict
import requests
import pandas as pd

# ISO3 codes we'll use
ISO3: Dict[str, str] = {
    "United Kingdom": "GBR",
    "United States": "USA",
    "Brazil": "BRA",
    "Japan": "JPN",
    "China": "CHN",
    "Germany": "DEU",
    "Switzerland": "CHE",
}

def fetch_worldbank_gdp(
    countries_iso3: List[str],
    start_year: int = 2000,
    end_year: int = 2022,
    indicator: str = "NY.GDP.MKTP.CD",
) -> pd.DataFrame:
    """
    Fetch annual GDP (default: current US$, NY.GDP.MKTP.CD) for multiple countries
    from the World Bank API.

    Returns a tidy DataFrame with columns: country, iso3, year, value
    """
    base = "https://api.worldbank.org/v2"
    country_str = ";".join(countries_iso3)
    url = (
        f"{base}/country/{country_str}/indicator/{indicator}"
        f"?format=json&per_page=20000&date={start_year}:{end_year}"
    )

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    records = data[1] if isinstance(data, list) and len(data) > 1 else []
    rows = []
    for r in records:
        val = r.get("value")
        if val is None:
            continue
        rows.append(
            {
                "country": r["country"]["value"],
                "iso3": r["country"]["id"],
                "year": int(r["date"]),
                "value": float(val),
            }
        )
    df = pd.DataFrame(rows).sort_values(["country", "year"]).reset_index(drop=True)
    return df

# --- add below your fetch function ---

import pandas as pd

def clean_gdp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep (country, iso3, year, value), drop NA, enforce dtypes, sort.
    Returns tidy long form.
    """
    out = (
        df[['country', 'iso3', 'year', 'value']]
        .dropna(subset=['value'])
        .astype({'year': 'int64', 'value': 'float64'})
        .sort_values(['country', 'year'])
        .reset_index(drop=True)
    )
    return out

def to_wide(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot to wide format: index=year, columns=country, values=value.
    """
    wide = (
        df.pivot(index='year', columns='country', values='value')
        .sort_index()
    )
    return wide

def plot_gdp(wide: pd.DataFrame, ax=None, title="GDP (current US$, 2000–2022)"):
    """
    Simple matplotlib line plot for multiple countries (trillions of USD).
    """
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))
    (wide / 1e12).plot(ax=ax)  # show in trillions for readability
    ax.set_ylabel("GDP (trillions, current US$)")
    ax.set_xlabel("Year")
    ax.set_title(title)
    ax.legend(title="Country", loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)
    return ax