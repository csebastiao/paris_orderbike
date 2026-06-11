# -*- coding: utf-8 -*-
"""
From the manually cleaned file, create the simplified bicycle network of Paris.
"""

import geopandas as gpd
import osmnx as ox
import momepy as mp
import networkx as nx

CRS_PARIS = "epsg:27571"
HIGHWAY_MAP = {
    "primary": "primary",
    "primary_link": "primary",
    "secondary": "secondary",
    "secondary_link": "secondary",
    "tertiary": "tertiary",
    "tertiary_link": "tertiary",
    "residential": "quaternary",
    "path": "quaternary",
}
FOLDEROOT = "./data/processed/map_matching_filt/"


def main():
    gdf = gpd.read_file(FOLDEROOT + "pes_to_osm_cleaned.gpkg")
    gdf = gdf.to_crs(CRS_PARIS)
    gdf = gdf[gdf["geometry"].notna()]
    # Simplify road hierarchy
    gdf["highway"] = gdf["highway"].map(HIGHWAY_MAP)
    G = mp.gdf_to_nx(gdf)
    # Remove interstitial nodes while keeping those where attributes change
    G_simp = ox.simplify_graph(
        nx.MultiDiGraph(G), edge_attrs_differ=["built_in", "level", "highway"]
    )
    gdf_nodes, gdf_edges = mp.nx_to_gdf(
        ox.convert.to_undirected(G_simp), points=True, lines=True
    )
    gdf_edges["length"] = gdf_edges.geometry.length
    gdf_nodes.to_file(FOLDEROOT + "nodes.gpkg")
    gdf_edges.to_file(FOLDEROOT + "edges.gpkg")


if __name__ == "__main__":
    main()
