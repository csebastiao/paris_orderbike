"""
Plot every additive growth strategies.
"""

import json
import os
import networkx as nx
import geopandas as gpd
import momepy as mp
from paris_orderbike.plot import plot_growth, plot_graph
from G_grow_bikenet import BUFF_SIZE, FOLDEROOT
from H_compute_real_growth_bikenet import TIMESTAMPS
from I_plot_lineplot import FOLDERPLOT


BUFFER = True
PLOT_METRICS = False
DPI = 100  # Larger means bigger files and longer to save, and there are a lot of pictures so quickly taking space and time
MET_LIST = [
    "coverage",
    "directness",
    "betweenness",
    "dual_betweenness",
    "closeness",
    "dual_closeness",
    "road_hierarchy",
    "road_hierarchy_coverage",
    "road_hierarchy_directness",
    "bikenet_hierarchy",
    "bikenet_hierarchy_coverage",
]
CHOICE = 0
# TODO add a way to plot also all relevant metrics below or somewhere, show the current step, and the number of kilometers built


def main():
    gdf_edges = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    G = mp.gdf_to_nx(gdf_edges, integer_labels=False, preserve_index=True)
    for end_folder in [
        # "Nothing",
        # "2021",
        "2026",
    ]:
        folder_data = FOLDEROOT + end_folder + "/"
        folder_plot = FOLDERPLOT + end_folder + "/growths/"
        if not os.path.exists(folder_plot):
            os.makedirs(folder_plot)
        for met in MET_LIST:
            foldermet = folder_data + f"bs_{BUFF_SIZE}_{met}/"
            foldermetplot = folder_plot + met + "/"
            if not os.path.exists(foldermetplot):
                os.makedirs(foldermetplot)
            if met in ["coverage", "random", "road_hierarchy", "bikenet_hierarchy"]:
                foldermet += f"{met}_{CHOICE:03}/"
            with open(foldermet + "order_growth.json") as f:
                order_growth = json.load(f)
            order_growth = [
                tuple((tuple(val[0]), tuple(val[1]), val[2])) for val in order_growth
            ]
            with open(foldermet + "metrics_growth.json") as f:
                metrics_dict = json.load(f)
            plot_growth(
                G,
                order_growth,
                foldermetplot,
                built=False,
                color_built="firebrick",
                color_added="steelblue",
                color_newest="darkgreen",
                node_size=8,
                buffer=BUFFER,
                buff_size=BUFF_SIZE,
                plot_metrics=PLOT_METRICS,
                growth_cov=metrics_dict["coverage"],
                growth_xx=metrics_dict["xx"],
                growth_dir=metrics_dict["directness"],
                dpi=DPI,
            )
        if end_folder == "Nothing":
            # Plot real growth
            folderrealplot = folder_plot + "real/"
            if not os.path.exists(folderrealplot):
                os.makedirs(folderrealplot)
            # Get boundaries for first edge to be in the right bbox
            _, ax = plot_graph(
                G,
                filepath=folderrealplot + "No.png",
                node_size=8,
                dpi=DPI,
                show=False,
                save=True,
                close=False,
            )
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()
            closeness = nx.closeness_centrality(G, distance="length")
            edge_closeness = {}
            for edge in G.edges:
                edge_closeness[edge] = (closeness[edge[0]] + closeness[edge[1]]) / 2
            init_edge = [tuple(max(edge_closeness, key=edge_closeness.get))]
            G_init = G.edge_subgraph(init_edge)
            plot_graph(
                G_init,
                filepath=folderrealplot + "0.png",
                node_size=8,
                dpi=DPI,
                show=False,
                save=True,
                close=True,
                bbox=[ymin, ymax, xmin, xmax],
            )
            for idx, t in enumerate(TIMESTAMPS[:-1]):
                H = G.edge_subgraph(
                    [
                        e
                        for e in G.edges
                        if G.edges[e]["built_in"] in TIMESTAMPS[: idx + 1]
                    ]
                )
                plot_graph(
                    H,
                    filepath=folderrealplot + t + ".png",
                    node_size=8,
                    dpi=DPI,
                    show=False,
                    save=True,
                    close=True,
                )


if __name__ == "__main__":
    main()
