# -*- coding: utf-8 -*-
"""
Extract the OSM graph of Paris.
"""

import geopandas as gpd
import pandas as pd

CRS_PARIS = "epsg:27571"
FOLDEROOT = "./data/processed/map_matching_filt/"


def main():
    segment_matches = gpd.read_file(FOLDEROOT + "segment_matches_20_17_30.gpkg")
    osm_segments = gpd.read_file(FOLDEROOT + "osm_segments_10.gpkg")
    osm_linestrings = gpd.read_file("./data/raw/osm/paris_edges_filt.gpkg")
    osm_linestrings["edge_id"] = osm_linestrings.reset_index().index
    # Join the two datasets, keeping only OSM geometry
    gdf_joined = pd.merge(
        segment_matches,
        osm_segments,
        left_on="matches_id",
        right_on="seg_id",
        how="inner",
        suffixes=("_ref", "_seg"),
    )
    # Join the segments with the full linestrings
    gdf_ls = pd.merge(
        osm_linestrings,
        gdf_joined,
        how="inner",
        right_on="edge_id_seg",
        left_on="edge_id",
        suffixes=("_ls", ""),
    )
    gdf_ls = gdf_ls[["street", "level", "built_in", "highway", "osmid", "geometry"]]
    # Remove duplicate linestrings
    gdf_ls["geometry"] = gdf_ls.normalize()
    gdf_ls = gdf_ls.drop_duplicates(subset=["level", "built_in", "highway", "geometry"])
    gdf_ls.to_file(FOLDEROOT + "pes_to_osm_raw.gpkg")


if __name__ == "__main__":
    main()
