# -*- coding: utf-8 -*-
"""
Extract the OSM graph of Paris.
"""

import os
import osmnx as ox
import city2graph as c2g

FOLDEROOT = "./data/raw/"
CRS_PARIS = "epsg:27571"
BUFF_SIZE = 200


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
    # Get OSM graph
    G = ox.graph_from_polygon(paris_poly_buffer)
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(
        G, nodes=True, node_geometry=True, edges=True, fill_edge_geometry=True
    )
    ox.save_graphml(G, folderpath_osm + "paris_graph.graphml")
    gdf_nodes.to_file(folderpath_osm + "paris_nodes.gpkg")
    gdf_edges.to_file(folderpath_osm + "paris_edges.gpkg")
    # Get Overture graph
    folderpath_ovt = FOLDEROOT + "ovt/"
    if not os.path.exists(folderpath_ovt):
        os.makedirs(folderpath_ovt)
    data = c2g.load_overture_data(
        area=paris_poly_buffer,
        types=["segment", "connector"],
        return_data=True,
        save_to_file=False,
    )
    data["segment"].to_file(folderpath_ovt + "paris_segments.gpkg")
    data["connector"].to_file(folderpath_ovt + "paris_connectors.gpkg")
    processed_segments = c2g.process_overture_segments(
        data["segment"].to_crs(CRS_PARIS),
        connectors_gdf=data["connector"].to_crs(CRS_PARIS),
        get_barriers=False,
        threshold=1.0,
    )
    processed_segments.to_file(folderpath_ovt + "paris_processed_segments.gpkg")


if __name__ == "__main__":
    main()
