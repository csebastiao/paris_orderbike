# -*- coding: utf-8 -*-
"""
Match the OSM data with the data from Paris en Selle. Reusing https://github.com/anerv/BikeDNA/blob/main/scripts/COMPARE/3b_extrinsic_analysis_feature_matching.ipynb.
"""

import os
import geopandas as gpd
import paris_orderbike.map_match as match_func

FOLDER_IN = "./data/raw/"
FOLDER_OUT = "./data/processed/"
CRS_PARIS = "epsg:27571"


def main():
    osm_edges_simplified = gpd.read_file(FOLDER_IN + "osm/paris_edges_filt.gpkg")
    osm_edges_simplified = osm_edges_simplified.to_crs(CRS_PARIS)
    osm_edges_simplified["edge_id"] = osm_edges_simplified.reset_index().index
    ref_edges_simplified = gpd.read_file(FOLDER_OUT + "pes_filtered.gpkg")
    ref_edges_simplified = ref_edges_simplified.to_crs(CRS_PARIS)
    ref_edges_simplified["edge_id"] = ref_edges_simplified.reset_index().index
    folderpath = FOLDER_OUT + "map_matching_filt/"
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    # Define feature matching user settings
    segment_length = 10  # The shorter the segments, the longer the matching process will take. For cities with a gridded street network with streets as straight lines, longer segments will usually work fine
    buffer_dist = 20
    hausdorff_threshold = 17
    angular_threshold = 30
    for s in [segment_length, buffer_dist, hausdorff_threshold, angular_threshold]:
        assert isinstance(s, int) or isinstance(s, float), print(
            "Settings must be integer or float values!"
        )
    osm_seg_fp = folderpath + f"osm_segments_{segment_length}.gpkg"
    ref_seg_fp = folderpath + f"ref_segments_{segment_length}.gpkg"
    if os.path.exists(osm_seg_fp) and os.path.exists(ref_seg_fp):
        osm_segments = gpd.read_file(osm_seg_fp)
        ref_segments = gpd.read_file(ref_seg_fp)
        print(
            "Segments have already been created! Continuing with existing segment data."
        )
        print("\n")
    else:
        print("Creating edge segments for OSM and reference data...")
        osm_segments = match_func.create_segment_gdf(
            osm_edges_simplified, segment_length=segment_length
        )
        osm_segments.rename(columns={"osmid": "org_osmid"}, inplace=True)
        osm_segments["osmid"] = osm_segments[
            "edge_id"
        ]  # Because matching function assumes an id column names osmid as unique id for edges
        osm_segments.set_crs(CRS_PARIS, inplace=True)
        osm_segments.dropna(subset=["geometry"], inplace=True)
        ref_segments = match_func.create_segment_gdf(
            ref_edges_simplified, segment_length=segment_length
        )
        ref_segments.set_crs(CRS_PARIS, inplace=True)
        ref_segments.rename(columns={"seg_id": "seg_id_ref"}, inplace=True)
        ref_segments.dropna(subset=["geometry"], inplace=True)
        print("Segments created successfully!")
        print("\n")
        osm_segments.to_file(osm_seg_fp)
        ref_segments.to_file(ref_seg_fp)
        print("Segments saved!")
    print(
        f"Starting matching process using a buffer distance of {buffer_dist} meters, a Hausdorff distance of {hausdorff_threshold} meters, and a max angle of {angular_threshold} degrees."
    )
    print("\n")
    buffer_matches = match_func.overlay_buffer(
        reference_data=ref_segments,
        osm_data=osm_segments,
        ref_id_col="seg_id_ref",
        osm_id_col="seg_id",
        dist=buffer_dist,
    )
    print("Buffer matches found! Continuing with final matching process...")
    print("\n")
    segment_matches = match_func.find_matches_from_buffer(
        buffer_matches=buffer_matches,
        osm_edges=osm_segments,
        reference_data=ref_segments,
        angular_threshold=angular_threshold,
        hausdorff_threshold=hausdorff_threshold,
    )
    print("Feature matching completed!")
    segment_matches.to_file(
        folderpath
        + f"segment_matches_{buffer_dist}_{hausdorff_threshold}_{angular_threshold}.gpkg"
    )


if __name__ == "__main__":
    main()
