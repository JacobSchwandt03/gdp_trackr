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