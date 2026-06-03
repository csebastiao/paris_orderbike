# -*- coding: utf-8 -*-
"""
Useful functions.
"""


def get_node_positions(G):
    """Find all node positions x (longitude) and y (latitude) from the graph G and put them into a numpy array."""
    return [[G.nodes[n]["x"], G.nodes[n]["y"]] for n in G.nodes]
