# -*- coding: utf-8 -*-
"""
Process the manually joined layers of Paris en Selle data.
"""

import geopandas as gpd

FOLDEROOT = "./data/processed/"
TIMESTAMPS = [
    "2023-05-17",
    "2023-10-01",
    "2024-01-15",
    "2024-04-04",
    "2024-08-22",
    "2024-12-22",
    "2025-06-02",
    "2026-01-28",
]
LEVEL_MAP = {
    "Primaire": "primary",
    "Secondaire": "secondary",
    "undefined": "secondary",  # Only for small portion
}


def main():
    gdf = gpd.read_file(FOLDEROOT + "pes_joined/8_layers.gpkg")
    # Remove useless columns
    gdf = gdf[
        ["Rue ou axe", "Etat", "Niveau", "geometry"]
        + [time + " Etat" for time in TIMESTAMPS[:-1]]
    ]
    # Filter streets outside of the plan
    gdf = gdf[gdf["Etat"] != "Hors Plan Vélo (Embellir)"]
    gdf = gdf.rename({"Rue ou axe": "street", "Niveau": "level"}, axis=1)
    # Merge status columns
    gdf["built_in"] = gdf.apply(merge_status_cols, axis=1)
    gdf["level"] = gdf["level"].map(LEVEL_MAP)
    gdf = gdf[["street", "level", "built_in", "geometry"]]
    gdf.to_file(FOLDEROOT + "pes_cleaned.gpkg")


def merge_status_cols(df):
    if df["Etat"] == "Réalisé Pré-2021":
        return "2021-01-01"
    for time in TIMESTAMPS[:-1]:
        if df[f"{time} Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé"]:
            return time
    if df["Etat"] in ["Réalisé dans le Plan Vélo", "Annoncé réalisé"]:
        return TIMESTAMPS[-1]
    return "No"


if __name__ == "__main__":
    main()
