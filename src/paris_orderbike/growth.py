# -*- coding: utf-8 -*-
"""
Class to grow a graph.
"""

import numpy as np
import networkx as nx
import momepy as mp
from .metrics import directness


class Orderbike:
    def __init__(
        self,
        G,
        preset="random",
        buff_size=200,
        built=False,
        keep_connected=True,
        seed=None,
    ):
        self.G = G.copy()
        self.gdf_edges = mp.nx_to_gdf(self.G, points=False, lines=True)
        self.preset = preset
        self.preset_dict = self._add_preset_dict()
        self.main_func, self.upda_func, self.type_func = self._use_preset()
        self.buff_size = buff_size
        self.seed = seed
        self.random_generator = np.random.default_rng(seed=self.seed)
        self.keep_connected = keep_connected
        self.built = built
        if self.built:
            self.G_init = self._build_graph()
        else:
            self.G_init = self._init_graph(preset)
        self.G_actual = self.G_init.copy()
        self.edges_actual = list(self.G_actual.edges)
        self.actual_buff_geom = mp.nx_to_gdf(
            self.G_actual, points=False, lines=True
        ).buffer(buff_size)
        self.max_area = self.gdf_edges.buffer(buff_size).union_all().area
        self.num_step = len(self.G.edges) - len(self.G_init.edges)
        self.directness = 0
        self.xx = 0
        self.num_cc = 0
        self.length_lcc = 0
        self.metrics_dict = {
            "xx": [],
            "directness": [],
            "coverage": [],
            "num_cc": [],
            "length_lcc": [],
        }
        self._compute_metrics()
        self.growth_order = []
        self.edges_tested = []
        self.values_found = []
        self.G_tested = None
        self.grown = False
        self.keep_searching = True

    def _add_preset_dict(self):
        return {
            "directness": {
                "main_func": self.main_directness,
                "upda_func": None,
                "type_func": "dynamic",
            },
            "coverage": {
                "main_func": self.main_coverage,
                "upda_func": self.upda_coverage,
                "type_func": "dynamic",
            },
            "betweenness": {
                "main_func": self.main_betweenness,
                "upda_func": None,
                "type_func": "static",
            },
            "closeness": {
                "main_func": self.main_closeness,
                "upda_func": None,
                "type_func": "static",
            },
            "hierarchy": {
                "main_func": self.main_hierarchy,
                "upda_func": None,
                "type_func": "static",
            },
            "random": {
                "main_func": self.main_random,
                "upda_func": None,
                "type_func": "static",
            },
        }

    def _use_preset(self):
        "Use a preset of functions instead of manually entering each of them."
        if self.preset not in self.preset_dict:
            raise ValueError(
                f"Preset not existing! Please choose between the following options: {list(self.preset_dict.keys())}"
            )
        else:
            return (
                self.preset_dict[self.preset]["main_func"],
                self.preset_dict[self.preset]["upda_func"],
                self.preset_dict[self.preset]["type_func"],
            )

    def _build_graph(self):
        "Use the built argument to initialize the graph with only a specific set of edges."
        return self.gdf_edges[self.gdf_edges["built"] == 1].index()

    def _init_graph(self, preset):
        "Initialize the graph with the edge of highest average closeness centrality."
        closeness = nx.closeness_centrality(self.G, distance="length")
        if preset == "hierarchy":
            max_hierarchy = self.gdf_edges["hierarchy"].max()
            edge_closeness = {
                edge: (closeness[edge[0]] + closeness[edge[1]]) / 2
                for edge in self.G.edges
                if self.G.edges[edge]["hierarchy"] == max_hierarchy
            }
        else:
            edge_closeness = {
                edge: (closeness[edge[0]] + closeness[edge[1]]) / 2
                for edge in self.G.edges
            }
        return self.G.edge_subgraph(
            [tuple(max(edge_closeness, key=edge_closeness.get))]
        )

    def _compute_metrics(self):
        self.directness = directness(self.G_actual)
        self.xx = sum([self.G_actual.edges[e]["length"] for e in self.edges_actual])
        self.actual_area = self.actual_buff_geom.union_all().area
        cc = list(nx.connected_components(self.G_actual))
        self.num_cc = len(cc)
        self.length_lcc = max(
            [
                sum(
                    [
                        self.G_actual.edges[e]["length"]
                        for e in self.G_actual.subgraph(comp).edges
                    ]
                )
                for comp in cc
            ]
        )
        self.metrics_dict["directness"].append(self.directness)
        self.metrics_dict["coverage"].append(self.actual_area)
        self.metrics_dict["xx"].append(self.xx)
        self.metrics_dict["num_cc"].append(self.num_cc)
        self.metrics_dict["length_lcc"].append(self.length_lcc)

    def grow(self):
        "Grow the network."
        if self.type_func == "dynamic":
            self._dynamic_growth()
        elif self.type_func == "static":
            self._static_growth()
        else:
            raise ValueError(
                "Wrong type_func value. type_func can only be either dynamic or static."
            )

    def _dynamic_growth(self):
        "Grow the network using a dynamic metric, recomputing metrics at each step for each valid edge."
        self.growth_order = []
        for _ in range(self.num_step):
            self.edges_tested = []
            self.values_found = []
            self.valid_edges = self._find_valid_edges()
            for edge in self.valid_edges:
                self.edges_tested.append(edge)
                self.G_tested = self.G.edge_subgraph(self.edges_actual + [edge])
                self.values_found.append(self.main_func())
            self._update_status(self._find_optimal_edge())
            if self.upda_func is not None:
                self.upda_func()
        self.grown = True

    def _find_optimal_edge(self):
        "Find the optimal edge."
        m = max(self.values_found)
        optimum = [
            edge for edge, val in zip(self.edges_tested, self.values_found) if val == m
        ]
        # When more than one optimal value, return a random value from all the optimal ones
        if len(optimum) > 1:
            # Need to change to list with built-in function to avoid numpy int type for values, and then to tuple for the list
            return optimum[self.random_generator.choice(len(optimum))]
        return optimum[0]

    def _static_growth(self):
        "Grow the network using a static metric, following the order for each valid edge."
        self.growth_order = []
        res = self.main_func()
        self.edges_tested = list(res.keys())
        self.values_found = np.array(list(res.values()))
        for _ in range(self.num_step):
            self.valid_edges = self._find_valid_edges()
            self._update_status(self._find_highest_rank())
        self.grown = True

    def _find_valid_edges(self):
        "Find all valid edges to add for a given step. For now work only if the final network do not have a component without built part."
        if self.keep_connected:
            return [
                edge
                for edge in self.G.edges
                if not (
                    (not any(node in self.G_actual for node in edge[:2]))
                    or edge in self.G_actual.edges
                )
            ]
        return [edge for edge in self.G.edges if edge not in self.G_actual.edges]

    def _find_highest_rank(self):
        for idx, edge in enumerate(self.edges_tested):
            if edge in self.valid_edges:
                value = self.values_found[idx]
                if len(np.where(self.values_found == value)[0]) > 1:
                    cand = [
                        self.edges_tested[pos]
                        for pos in np.where(self.values_found == value)[0]
                        if self.edges_tested[pos] in self.valid_edges
                    ]
                    return cand[self.random_generator.choice(len(cand))]
                return edge

    def _update_status(self, choice):
        self.growth_order.append(choice)
        self.edges_actual.append(choice)
        self.G_actual = self.G.edge_subgraph(self.edges_actual)
        self.actual_buff_geom.loc[len(self.actual_buff_geom) + 1] = self.G.edges[
            choice
        ]["geometry"].buffer(self.buff_size)
        self._compute_metrics()

    def get_metrics_dict(self):
        return self.metrics_dict

    def get_growth_order(self):
        return self.growth_order

    def main_directness(self):
        return directness(self.G_tested)

    def main_coverage(self):
        if self.keep_searching:
            edge = self.edges_tested[0]
            geom_test = self.actual_buff_geom.copy()
            geom_test.loc[len(self.actual_buff_geom) + 1] = self.G.edges[edge][
                "geometry"
            ].buffer(self.buff_size)
            test_area = geom_test.geometry.union_all().area
            return (test_area - self.actual_area) / self.G.edges[edge]["length"]
        else:
            return 0

    def upda_coverage(self):
        if self.actual_area == self.max_area:
            self.keep_searching = False

    def main_betweenness(self):
        return {
            key: val
            for key, val in sorted(
                nx.edge_betweenness_centrality(self.G, weight="length").items(),
                key=lambda x: x[1],
                reverse=True,
            )
        }

    def main_closeness(self):
        nclo = nx.closeness_centrality(self.G, distance="length")
        return {
            key: val
            for key, val in sorted(
                {e: (nclo[e[0]] + nclo[e[1]]) / 2 for e in self.G.edges}.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        }

    def main_hierarchy(self):
        return {edge: self.G.edges[edge]["hierarchy"] for edge in self.G.edges}

    def main_random(self):
        edgelist = list(self.G.edges)
        self.random_generator.shuffle(edgelist)
        return {key: -idx for idx, key in enumerate(edgelist)}
