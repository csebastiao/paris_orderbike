"""
Add Gini coefficient for share of bicycle lane in each borough for all orders.
"""

import json

import geopandas as gpd
import numpy as np
from Ga_grow_bikenet import NUM_COV_TRIAL, NUM_HIER_TRIAL, NUM_RAND_TRIAL, init_gdf
from I_grow_random_real_bikenet import NUM_RAND_REAL_TRIAL

FOLDEROOT = "./data/processed/"
BUFF_SIZE = 400
MET = [
    # "directness",
    # "coverage",
    # "road_hierarchy",
    # "random",
    # "betweenness",
    # "closeness",
    # "dual_betweenness",
    # "dual_closeness",
    # "road_hierarchy_coverage",
    # "road_hierarchy_directness",
    # "real_random",
    "real",
    # "random_disconnected",
    # "random_relaxed",
]
TRIAL_DICT = {
    "coverage": NUM_COV_TRIAL,
    "road_hierarchy": NUM_HIER_TRIAL,
    "random": NUM_RAND_TRIAL,
    "random_relaxed": NUM_RAND_TRIAL,
    "random_disconnected": NUM_RAND_TRIAL,
    "real_random": NUM_RAND_REAL_TRIAL,
}
TIMESTAMPS = [
    "2021-01-01",
    "2023-05-17",
    "2023-10-01",
    "2024-01-15",
    "2024-04-04",
    "2024-08-22",
    "2024-12-22",
    "2025-06-02",
    "2026-01-28",
    "No",
]
START_TIMESTAMPS = {
    "Nothing": 0,
    "2021": 1,
    "2026": 9,
}
RECOMPUTE = True


def main():
    for end_folder in ["2021", "2026", "Nothing"]:
        gdf_bikenet = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
        gdf_arr = gpd.read_file(FOLDEROOT + "paris_arr_pop.gpkg")
        gdf_arr_buff = gdf_arr.to_crs(gdf_bikenet.crs)
        gdf_arr_buff["geometry"] = gdf_arr_buff.geometry.buffer(50)
        gdf_sjoin = gdf_bikenet.sjoin(gdf_arr_buff)
        gdf_bikenet["in_arrs"] = gdf_sjoin.groupby(by=gdf_sjoin.index)[
            "arrondissement"
        ].apply(list)
        gdf_bikenet["eff_length"] = gdf_bikenet["length"] / gdf_bikenet["in_arrs"].map(
            len
        )
        for met in MET:
            if met in [
                "coverage",
                "road_hierarchy",
                "random",
                "real_random",
                "random_disconnected",
                "random_relaxed",
            ]:
                num_trials = TRIAL_DICT[met]
                for i in range(num_trials):
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/{met}_{i:03}/order_growth.json"
                    ) as f:
                        order_growth = json.load(f)
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/{met}_{i:03}/metrics_growth.json"
                    ) as f:
                        met_dict = json.load(f)
                    if "gini" not in met_dict or RECOMPUTE:
                        met_dict["gini"] = compute_gini_order(
                            gdf_bikenet, gdf_arr_buff, order_growth
                        )
                        with open(
                            FOLDEROOT
                            + end_folder
                            + f"/bs_{BUFF_SIZE}_{met}/{met}_{i:03}/metrics_growth.json",
                            "w",
                        ) as f:
                            json.dump(met_dict, f)
            elif met == "real":
                with open(
                    FOLDEROOT
                    + end_folder
                    + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json"
                ) as f:
                    met_dict = json.load(f)
                if "gini" not in met_dict or RECOMPUTE:
                    start_end = START_TIMESTAMPS[end_folder]
                    gdf_edges = init_gdf(gdf_bikenet, end_folder)
                    gdf_edges = gdf_edges[gdf_edges["built"] == 1]
                    real_ginis = [compute_gini(gdf_edges, gdf_arr_buff)]
                    for i in range(len(TIMESTAMPS[start_end:])):
                        gdf_edges = gdf_bikenet[
                            gdf_bikenet["built_in"].isin(
                                TIMESTAMPS[: start_end + i + 1]
                            )
                        ]
                        real_ginis.append(compute_gini(gdf_edges, gdf_arr_buff))
                    met_dict["gini"] = real_ginis
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json",
                        "w",
                    ) as f:
                        json.dump(met_dict, f)
            else:
                with open(
                    FOLDEROOT + end_folder + f"/bs_{BUFF_SIZE}_{met}/order_growth.json"
                ) as f:
                    order_growth = json.load(f)
                with open(
                    FOLDEROOT
                    + end_folder
                    + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json"
                ) as f:
                    met_dict = json.load(f)
                if "gini" not in met_dict or RECOMPUTE:
                    met_dict["gini"] = compute_gini_order(
                        gdf_bikenet, gdf_arr_buff, order_growth
                    )
                    with open(
                        FOLDEROOT
                        + end_folder
                        + f"/bs_{BUFF_SIZE}_{met}/metrics_growth.json",
                        "w",
                    ) as f:
                        json.dump(met_dict, f)


def compute_gini_order(gdf_edges, gdf_arr, order_growth):
    gdf_end = gdf_edges.copy()
    gdf_arr_cop = gdf_arr.copy()
    gdf_arr_cop["lkm"] = 0.0
    gdf_arr_cop["lkmpkms"] = 0.0
    # Make order growth readable
    order_growth = [(tuple(val[0]), tuple(val[1]), val[2]) for val in order_growth]
    # Swap u and v to find all edges
    order_growth_rev = [(tuple(val[1]), tuple(val[0]), val[2]) for val in order_growth]
    order_dict = {val: idx for idx, val in enumerate(order_growth)}
    order_dict_rev = {val: idx for idx, val in enumerate(order_growth_rev)}
    # Transfrom strings into tuple of float
    gdf_end["from"] = gdf_end["from"].apply(
        lambda x: (float(x.split(",")[0][1:]), float(x.split(",")[1][1:-1]))
    )
    gdf_end["to"] = gdf_end["to"].apply(
        lambda x: (float(x.split(",")[0][1:]), float(x.split(",")[1][1:-1]))
    )
    gdf_end["key"] = gdf_end.apply(lambda df: (df["from"], df["to"], 0), axis=1)
    # Find order of growth for list of edges
    gdf_end["order"] = gdf_end["key"].map(order_dict)
    gdf_end["order_rev"] = gdf_end["key"].map(order_dict_rev)
    gdf_end["order_comb"] = gdf_end["order"].fillna(gdf_end["order_rev"])
    gdf_end["order_comb"] = gdf_end["order_comb"].fillna(-1).map(int)
    gdf_end = gdf_end.sort_values(by="order_comb")
    # Remove useless columns
    gdf_end = gdf_end[
        ["level", "order_comb", "length", "eff_length", "in_arrs", "geometry"]
    ]
    # Initialize with edges built in the beginning
    gdf_built = gdf_end[gdf_end["order_comb"] == -1]
    # Add edges to the corresponding arrs
    for row in gdf_built.itertuples(index=False):
        gdf_arr_cop.loc[gdf_arr_cop["arrondissement"].isin(row.in_arrs), "lkm"] += (
            row.eff_length / 10**3
        )
    gdf_arr_cop["lkmpkms"] = gdf_arr_cop["lkm"] / gdf_arr_cop["area"]
    gini_vals = [gini(gdf_arr_cop["lkmpkms"])]
    for row in gdf_end[gdf_end["order_comb"] > -1].itertuples(index=False):
        gdf_arr_cop.loc[gdf_arr_cop["arrondissement"].isin(row.in_arrs), "lkm"] += (
            row.eff_length / 10**3
        )
        gdf_arr_cop.loc[gdf_arr_cop["arrondissement"].isin(row.in_arrs), "lkmpkms"] = (
            gdf_arr_cop.loc[gdf_arr_cop["arrondissement"].isin(row.in_arrs), "lkm"]
            / gdf_arr_cop.loc[gdf_arr_cop["arrondissement"].isin(row.in_arrs), "area"]
        )
        gini_vals.append(gini(gdf_arr_cop["lkmpkms"].values))
    return gini_vals


def compute_gini(gdf_edges, gdf_arr):
    """Compute the Gini coefficient of distribution of edges on polygons, normalized by their area."""
    gdf_sjoin = gdf_arr.sjoin(gdf_edges)
    gdf_sjoin["eff_length"] = gdf_sjoin["length"] / gdf_sjoin["index_right"].map(
        gdf_sjoin["index_right"].value_counts()
    )
    gdf_sjoin = gdf_sjoin.dissolve(
        by="arrondissement", aggfunc={"eff_length": "sum", "area": "first"}
    )
    arr_vals = gdf_sjoin["eff_length"] / gdf_sjoin["area"]
    return gini(arr_vals)


# Function from https://github.com/oliviaguest/gini
def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    array = np.sort(array)  # values must be sorted
    index = np.arange(1, array.shape[0] + 1)  # index per array element
    n = array.shape[0]  # number of array elements
    return (np.sum((2 * index - n - 1) * array)) / (
        n * np.sum(array)
    )  # Gini coefficient


if __name__ == "__main__":
    main()
