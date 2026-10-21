"""
Plot map of the bicycle network, showing either the road hierarchy next to the bicycle lanes or the time that the bicycle lane was built.
"""

import json

import geopandas as gpd
import matplotlib as mpl
import momepy as mp
import numpy as np
from Ga_grow_bikenet import FOLDEROOT
from H_grow_linear_real_bikenet import TIMESTAMPS
from Ka_plot_lineplot_covdir_merged_2021_main import FOLDERPLOT_MAIN
from matplotlib import pyplot as plt
from matplotlib_map_utils.core.scale_bar import scale_bar

BUFF_SIZE = 400
FIGSIZE = [11.69 * 3, 8.27]
TITLES = ["Empirical", "Hierarchy-coverage", "Dual betweenness"]
PARAMS_DICT = {
    "rcparams": {
        "font.size": 40,
        "font.family": "sans-serif",
        "font.sans-serif": "Arial",
        "legend.loc": "upper left",
        "legend.frameon": False,
        "figure.dpi": 200,
    },
}
COLOR_OLD = "black"
COLOR_NEW = "black"


def main():
    for key in PARAMS_DICT["rcparams"]:
        mpl.rcParams[key] = PARAMS_DICT["rcparams"][key]
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    size_int = gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:-1])]["length"].sum()
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    fig, axs = plt.subplots(1, 3, figsize=FIGSIZE)
    for idx, met in enumerate(["real", "road_hierarchy_coverage", "dual_betweenness"]):
        ax = axs[idx]
        ax.set_title(TITLES[idx])
        foldermet = FOLDEROOT + f"2021/bs_{BUFF_SIZE}_{met}/"
        if idx == 0:
            scale_bar(
                ax,
                location="lower left",
                aob={"bbox_to_anchor": (-0.06, -0.08), "bbox_transform": ax.transAxes},
                style="ticks",
                bar={
                    "projection": gdf_edges.crs,
                    "unit": "km",
                    "major_mult": 1,
                    "major_div": 3,
                    "height": 0.2,
                },
                units={"fontsize": PARAMS_DICT["rcparams"]["font.size"] * 0.8},
                labels={
                    "style": "first_last",
                    "fontsize": PARAMS_DICT["rcparams"]["font.size"] * 0.8,
                    "sep": 0.05,
                },
            )
            gdf_edges[gdf_edges["built_in"].isin(TIMESTAMPS[:-1])].plot(
                ax=ax,
                color="black",
                linewidth=3,
                zorder=4,
                capstyle="round",
                joinstyle="round",
            )
            ax.axis("off")
        else:
            with open(foldermet + "order_growth.json") as f:
                order_growth = json.load(f)
            order_growth = [
                (tuple(val[0]), tuple(val[1]), val[2]) for val in order_growth
            ]
            with open(foldermet + "metrics_growth.json") as f:
                metrics_growth = json.load(f)
            gdf_edges[gdf_edges["built_in"] == TIMESTAMPS[0]].plot(
                ax=ax,
                color="black",
                linewidth=3,
                zorder=4,
                capstyle="round",
                joinstyle="round",
            )
            idx_stage = find_closest_value_idx(metrics_growth["xx"], size_int)
            H = G.edge_subgraph(order_growth[: idx_stage + 2])
            temp_gdf_edges = mp.nx_to_gdf(H, points=False, lines=True)
            temp_gdf_edges.plot(
                ax=ax,
                color="black",
                zorder=5,
                linewidth=3,
                capstyle="round",
                joinstyle="round",
            )
            ax.axis("off")
    fig.subplots_adjust(wspace=-0.075)
    fig.savefig(
        FOLDERPLOT_MAIN + "Bikenet_2021_real_hc_db.png",
        bbox_inches="tight",
        pad_inches=0.06,
    )
    plt.close(fig=fig)


def find_closest_value_idx(list_values, target_value):
    lst = np.asarray(list_values)
    return (np.abs(lst - target_value)).argmin()


if __name__ == "__main__":
    main()
