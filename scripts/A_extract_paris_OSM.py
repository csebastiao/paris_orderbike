# -*- coding: utf-8 -*-
"""
Extract the OSM graph of Paris.
"""

import os
import osmnx as ox

FOLDEROOT = "./data/raw/"
CRS_PARIS = "epsg:27571"
BUFF_SIZE = 200
HIGHWAY_TAGS = [
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "residential",
]


def main():
    folderpath_osm = FOLDEROOT + "osm/"
    if not os.path.exists(folderpath_osm):
        os.makedirs(folderpath_osm)
    # Buffer Paris boundaries to get surrounding streets
    paris_poly_gdf = ox.geocode_to_gdf("R7444", by_osmid=True)
    paris_poly_gdf = paris_poly_gdf.to_crs(CRS_PARIS)
    paris_poly_gdf.to_file(FOLDEROOT + "paris_boundaries.gpkg")
    paris_poly_buffer = paris_poly_gdf.geometry.buffer(BUFF_SIZE)
    paris_poly_buffer = paris_poly_buffer.to_crs(epsg=4326).geometry.values[0]
    # Get OSM graph, full
    G = ox.graph_from_polygon(paris_poly_buffer, simplify=False)
    G = ox.simplify_graph(G, edge_attrs_differ=["highway"])
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(
        G, nodes=True, node_geometry=True, edges=True, fill_edge_geometry=True
    )
    ox.save_graphml(G, folderpath_osm + "paris_graph.graphml")
    gdf_nodes.to_file(folderpath_osm + "paris_nodes.gpkg")
    gdf_edges.to_file(folderpath_osm + "paris_edges.gpkg")
    # Filter only edges of specific highway tags
    gdf_edges_filt = gdf_edges[gdf_edges["highway"].isin(HIGHWAY_TAGS)]
    gdf_edges_filt.to_file(folderpath_osm + "paris_edges_filt.gpkg")
    # Get OSM graph, drive only
    G = ox.graph_from_polygon(paris_poly_buffer, simplify=False, network_type="drive")
    G = ox.simplify_graph(G, edge_attrs_differ=["highway"])
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(
        G, nodes=True, node_geometry=True, edges=True, fill_edge_geometry=True
    )
    ox.save_graphml(G, folderpath_osm + "paris_car_graph.graphml")
    gdf_nodes.to_file(folderpath_osm + "paris_car_nodes.gpkg")
    gdf_edges.to_file(folderpath_osm + "paris_car_edges.gpkg")


if __name__ == "__main__":
    main()
