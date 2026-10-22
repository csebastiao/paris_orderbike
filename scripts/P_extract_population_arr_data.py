"""
Extract population data in Paris and the Small Crown around it from raw INSEE data.
"""

import geopandas as gpd
import pandas as pd

FOLDER_IN = "./data/raw/insee/"
FOLDER_OUT = "./data/processed/"


def main():
    df_iris_pop = pd.read_csv(
        FOLDER_IN + "IRIS_population_2021/base-ic-evol-struct-pop-2021.CSV",
        delimiter=";",
        low_memory=False,
    )
    df_iris_pop = df_iris_pop.rename({"IRIS": "CODE_IRIS"}, axis=1)
    gdf_iris = gpd.read_file(
        FOLDER_IN
        + "IRIS_geometry_2021/IRIS-GE/1_DONNEES_LIVRAISON_2021-06-00135/IRIS-GE_2-0_SHP_LAMB93_FXX-2021/IRIS_GE.SHP"
    )
    gdf_iris = gdf_iris.to_crs(epsg=4326)
    gdf_iris["dep"] = gdf_iris["CODE_IRIS"].apply(lambda x: str(x)[:2])
    gdf_psc_iris = gdf_iris[gdf_iris["dep"].isin(["75", "92", "93", "94"])]
    gdf_psc_iris = gdf_psc_iris[["CODE_IRIS", "geometry"]]
    gdf_psc_iris = gdf_psc_iris.merge(df_iris_pop, on="CODE_IRIS")
    gdf_psc_iris = gdf_psc_iris.to_crs(gdf_psc_iris.estimate_utm_crs())
    gdf_psc_iris["arrondissement"] = gdf_psc_iris["CODE_IRIS"].apply(
        lambda x: int(x[3:5]) if x[:2] == "75" else 99
    )
    gdf_psc_iris["area"] = gdf_psc_iris.geometry.area / 10**6
    gdf_psc_iris["pop_density"] = gdf_psc_iris.apply(
        lambda df: df.P21_POP / df.area, axis=1
    )
    gdf_psc_iris = gdf_psc_iris.to_crs(epsg=4326)
    gdf_psc_iris = gdf_psc_iris[
        ["CODE_IRIS", "arrondissement", "P21_POP", "pop_density", "area", "geometry"]
    ]
    gdf_psc_iris = gdf_psc_iris.rename({"P21_POP": "pop"}, axis=1)
    gdf_psc_iris.to_file(FOLDER_OUT + "IRIS_pop_psc.gpkg")
    gdf_paris = gdf_psc_iris[gdf_psc_iris["arrondissement"] < 99][
        ["arrondissement", "pop", "geometry"]
    ]
    # Merge 1st to 4th arrondissement
    gdf_paris.loc[gdf_paris.arrondissement.isin([1, 2, 3, 4]), "arrondissement"] = 1
    gdf_arr = gdf_paris.dissolve(
        by="arrondissement",
        aggfunc={"pop": "sum"},
    )
    gdf_arr = gdf_arr.to_crs(gdf_arr.estimate_utm_crs())
    gdf_arr["area"] = gdf_arr.geometry.area / 10**6
    # Remove parks from area of the  and 12th arrondissements
    gdf_arr.loc[12, "area"] -= gdf_psc_iris[
        gdf_psc_iris["CODE_IRIS"].isin(["751124577", "751124677"])
    ]["area"].sum()
    gdf_arr.loc[16, "area"] -= gdf_psc_iris[
        gdf_psc_iris["CODE_IRIS"].isin(["751166177", "751166277", "751166377"])
    ]["area"].sum()
    gdf_arr.to_crs(epsg=4326)
    gdf_arr.to_file(FOLDER_OUT + "paris_arr_pop.gpkg")


if __name__ == "__main__":
    main()
