# -*- coding: utf-8 -*-
"""
Simplify the OSM graph of Paris using neatnet.
"""

import geopandas as gpd
import neatnet

FOLDER_IN = "./data/raw/osm/"
FOLDER_OUT = "./data/processed/"
CRS_PARIS = "epsg:27571"


def main():
    gdf_edges = gpd.read_file(FOLDER_IN + "paris_car_edges.gpkg")
    # Neatify car network
    gdf_edges_simp = neatnet.neatify(gdf_edges.to_crs(CRS_PARIS))
    gdf_edges_simp["new_ind"] = gdf_edges_simp.reset_index.index()
    gdf_edges_simp.to_file(FOLDER_OUT + "paris_car_edges_neatified.gpkg")


if __name__ == "__main__":
    main()
