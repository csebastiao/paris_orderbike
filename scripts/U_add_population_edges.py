"""
Add population data on edges. This is a simplified assumption where we assume that
population is covered at the street level. Having instead a field on which population
is covered if infrastructure is close enough would be too heavy compute-wise.
"""

from functools import partial
from multiprocessing import Pool

import geopandas as gpd
import momepy as mp
import numpy as np
import shapely
import tqdm
from Ga_grow_bikenet import FOLDEROOT
from geopandas import GeoDataFrame
from matplotlib import pyplot as plt
from numpy import linspace, vstack
from osmnx import graph_to_gdfs, plot_graph
from osmnx.projection import is_projected
from pandas import Series
from scipy.spatial import Voronoi
from shapely import Polygon, get_coordinates, line_interpolate_point, polygons
from shapely.lib import GEOSException

BUFFER_SIZE = 400


def main():
    gdf_bikenet = gpd.read_file(FOLDEROOT + "bikenet_edges.gpkg")
    bikenet_limit = shapely.Polygon(
        gdf_bikenet.geometry.union_all().buffer(BUFFER_SIZE).exterior
    )
    gdf_pop = gpd.read_file(FOLDEROOT + "IRIS_pop_psc.gpkg")
    gdf_pop = gdf_pop.to_crs(gdf_bikenet.crs)
    G = mp.gdf_to_nx(gdf_bikenet, integer_labels=False, preserve_index=True)
    add_edge_cells(G, limit=bikenet_limit)
    gdf_edges = mp.nx_to_gdf(G, lines=True, points=False)
    gdf_edges["geometry"] = gdf_edges["cell"]
    gdf_edges_pop = put_population_on_poly(gdf_edges, gdf_pop, batch_size=1000)
    gdf_edges_pop.to_file(FOLDEROOT + "gdf_edges_pop.gpkg")
    gdf_bikenet["pop"] = gdf_edges_pop["pop"]
    gdf_bikenet["pop_pkm"] = 10**3 * gdf_bikenet["pop"] / gdf_bikenet["length"]
    gdf_bikenet.to_file(FOLDEROOT + "bikenet_wpop_edges.gpkg")


# Functions from https://github.com/NERDSITU/superblockify
def put_population_on_poly(polygons, population_blocks, batch_size=10000):
    """
    Put the population from census block data to polygons tiling

    Args:
        polygons (geopandas.GeoDataFrame): hexagon tiling.
        population_blocks (geopandas.GeoDataFrame): population from census blocks.
        batch_size (int, optional): Size of batches for multiprocessing. Defaults to 10000.

    Returns:
        geopandas.GeoDataFrame: polygons with the population count.
    """
    population_blocks_index = shapely.STRtree(population_blocks.geometry)
    # Add columns for population and area
    polygons["pop"] = 0.0
    batch_size = int(min(batch_size, len(polygons)))
    with Pool() as pool:
        slices = (
            slice(n_batch * batch_size, min((n_batch + 1) * batch_size, len(polygons)))
            for n_batch in range(len(polygons) // batch_size + 1)
        )

        population_sums = list(
            tqdm.tqdm(
                pool.imap_unordered(
                    partial(
                        _population_fraction_list_sliced,
                        population_blocks["geometry"].values,
                        population_blocks["pop"].values,
                        population_blocks_index,
                        polygons["geometry"].values,
                    ),
                    slices,
                ),
                desc="Distributing population over road cells",
                total=len(population_blocks) // batch_size + 1,
                unit="Cells",
                unit_scale=batch_size,
                unit_divisor=batch_size,
            )
        )
        # write the results to the dataframe
        for _, (cell_slice, population) in enumerate(population_sums):
            polygons.loc[polygons.index[cell_slice], "pop"] = population
    return polygons


def population_fraction(polygon, population, road_cell):
    """Function returns fractional population count between road_cell and
    polygon.

    Parameters
    ----------
    polygon : shapely.geometry.Polygon
        Polygon of cell.
    population : float
        Population of cell.
    road_cell : shapely.geometry.Polygon
        Polygon of road cell.

    Returns
    -------
    float
        Fractional population count between road_cell and polygon.
    """
    intersection = road_cell.intersection(polygon)
    return population * intersection.area / polygon.area


def _population_fraction_list(
    polygons, populations, overlap_index_pairs, road_cell_geometries
):  # pragma: no cover
    """Function returns population count for each road cell in road_cell_geometries

    Parameters
    ----------
    polygons : list of shapely.geometry.Polygon
        List of cells.
    populations : list of float
        List of populations.
    overlap_index_pairs : ndarray with shape (2, n)
        Array of indices of overlapping road cells and cells.
        The first row contains the indices of the road cells, and the second row
        contains the indices of the cells.
    road_cell_geometries : list of shapely.geometry.Polygon

    Returns
    -------
    ndarray with shape (n,)
        Array of population counts for each road cell in road_cell_geometries.
    """
    population = np.zeros(len(road_cell_geometries))
    for road_cell_idx, pop_cell_idx in overlap_index_pairs:
        population[road_cell_idx] += population_fraction(
            polygons[pop_cell_idx],
            populations[pop_cell_idx],
            road_cell_geometries[road_cell_idx],
        )
    return population


def _population_fraction_list_sliced(
    polygons, populations, polygons_index, road_cell_geometries, slice_n
):
    """Function for the parallelization of _population_fraction_list.

    Works like :func:`_population_fraction_list`, but takes all the road cells
    and only determines the population for the road cells in slice_n.

    Parameters
    ----------
    polygons : list of shapely.geometry.Polygon
        List of cells.
    populations : list of float
        List of populations.
    polygons_index : shapely.strtree.STRtree
        STRtree index of polygons.
    road_cell_geometries : list of shapely.geometry.Polygon
        List of road cells.
    slice_n : slice
        Slice of road cells to determine the population for.

    Returns
    -------
    slice, ndarray with shape (n,)
        Slice of road cells and array of population counts for each road cell in
        road_cell_geometries[slice_n].
    """
    return slice_n, _population_fraction_list(
        polygons,
        populations,
        polygons_index.query(road_cell_geometries[slice_n], predicate="intersects").T,
        road_cell_geometries[slice_n],
    )


def add_edge_cells(graph, **tess_kwargs):
    """Add edge tessellation cells to edge attributes in the graph.

    Tessellates the graph into plane using a Voronoi cell approach.
    Function writes to edge attribute `cells` of the graph in-place.
    Furthermore, `cell_id` is added to the edge attributes, for easier summary of
    statistics later.

    The approach was developed inspired by the :class:`momepy.Tessellation` class
    and tessellates with :class:`scipy.spatial.Voronoi`.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The graph to tessellate.
    **tess_kwargs
        Keyword arguments for the
        :func:`superblockify.population.tessellation.get_edge_cells` function.

    Raises
    ------
    ValueError
        If the graph is not in a projected coordinate system.
    ValueError
        If the limit and the edge points are disjoint.

    Notes
    -----
    The graph must be in a projected coordinate system.
    """
    edge_cells = get_edge_cells(graph, **tess_kwargs)
    # Add cells to graph (in-place)
    for edge_keys, polygon in edge_cells.geometry.items():
        for edge_key in edge_keys:
            graph.edges[edge_key]["cell"] = polygon
            graph.edges[edge_key]["cell_id"] = edge_cells.index.get_loc(edge_keys)


def get_edge_cells(graph, limit=None, segment=25, show_plot=False):
    """Get edge tessellation cells for the graph.

    Tessellates the graph into plane using a Voronoi cell approach.

    The approach was developed inspired by the :class:`momepy.Tessellation` class
    and tessellates with :class:`scipy.spatial.Voronoi`.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The graph to tessellate.
    limit : shapely.geometry.Polygon or None
        The limit of the tessellation. Must be in the same CRS as the graph.
        If None, it will be calculated as the exterior of the 100m buffered unary
        union of the graph's edges.
    segment : float
        The maximum distance for the point interpolation. Default is 25.
    show_plot : bool
        If True, a plot of the tessellation will be shown. Default is False.

    Returns
    -------
    geopandas.GeoDataFrame
        A GeoDataFrame with the tuple of edge keys as index and the tessellation
        cells as geometry.

    Raises
    ------
    ValueError
        If the graph is not in a projected coordinate system.
    ValueError
        If the limit and the edge points are disjoint.

    Notes
    -----
    The graph must be in a projected coordinate system.
    """
    # Check if the graph is projected
    if not is_projected(graph.graph["crs"]):
        raise ValueError(
            "The graph must be in a projected coordinate system. "
            "Use `osmnx.project_graph` to project the graph."
        )
    edges = get_edge_polygons(graph)
    # Make limit polygon
    if limit is None:
        limit = Polygon(edges.union_all().buffer(100).exterior)
    else:
        # Check if limit and edges are disjoint
        if limit.disjoint(edges.union_all()):
            raise ValueError(
                "The limit and the edge points are disjoint. "
                "Please provide a limit that intersects the edges."
            )

    # Convert edges to points and their multiindex
    edge_points, edge_indices = edges_to_points(edges, segment=segment)
    # Convert limit hull to points
    hull_points = line_interpolate_point(
        limit.boundary,
        linspace(
            0.1,
            limit.length - 0.1,
            num=int((limit.length - 0.1) // segment),
        ),
    )
    # Add to point array
    edge_points = vstack([edge_points, get_coordinates(hull_points)])
    edge_indices += [-1] * len(hull_points)
    # Create Voronoi tessellation
    edge_voronoi_diagram = Voronoi(edge_points)
    # Reconstruct edge cells from Voronoi point tessellation
    edge_cells = reconstruct_edge_cells(
        edge_voronoi_diagram, edge_indices, graph.graph["crs"]
    )
    # Plot tessellation
    if show_plot:
        fig, axe = plt.subplots(figsize=(8, 8))
        edge_cells.to_crs(graph.graph["crs"]).plot(
            ax=axe, cmap="tab20", edgecolor="white", alpha=0.5
        )
        plot_graph(graph, ax=axe, node_size=0, edge_color="black", edge_linewidth=0.5)
        axe.set_axis_off()
        axe.set_title("Edge tessellation")
        fig.tight_layout()
    return edge_cells


def get_edge_polygons(graph):
    """Prepare edge polygons for tessellation.

    This returns a GeoDataFrame where edges with same start and end node are
    merged, if their geometry is equal or a reversed version of the other.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        The graph to tessellate.

    Returns
    -------
    edges : geopandas.GeoDataFrame
        The edges with their polygons.
    """
    edges = graph_to_gdfs(
        graph, nodes=False, edges=True, node_geometry=False, fill_edge_geometry=True
    )

    # Merge two columns, when the geometry of one is equal or the reverse of the other
    # 1. Group edge ig (u, v) == (v, u) or (u, v) == (u, v)
    # Match by node pair (u, v) where u < v
    # get flat index of the first match
    edges["edge_id"] = edges.index.to_flat_index()
    # sort the edge_id tuples
    edges["node_pair"] = edges["edge_id"].apply(lambda x: tuple(sorted(x[:2])))
    # 2. Aggregate if the geometry is equal or the reverse of the other
    # Merge columns if geometry_1 == geometry_2 or geometry_1 == geometry_2.reverse()
    # reverse geometry if x_start >= x_end (analogous to sorted node_pair)
    edges["geometry"] = edges["geometry"].apply(
        lambda x: x if x.coords[0] < x.coords[-1] else x.reverse()
    )
    # 3. Group by node_pair and geometry, aggregate edge_id
    edges = (
        edges.groupby(["node_pair", "geometry"])
        .agg(
            {
                "edge_id": tuple,  # tuple of edge indices
            }  # tuple, because it is immutable and thus hashable for indexing
        )
        .reset_index()
    )
    edges.set_index("edge_id", inplace=True)
    edges.drop(columns=["node_pair"], inplace=True)
    return GeoDataFrame(edges, geometry="geometry", crs=graph.graph["crs"])


def edges_to_points(edges, segment=25):
    """Convert edges to points.

    Parameters
    ----------
    edges : geopandas.GeoDataFrame
        The edges to convert to points.
    segment : float
        The maximum distance for the point interpolation. Default is 25.

    Returns
    -------
    points : geopandas.GeoDataFrame
        The points.
    indices : list of int
        The indices of the points in the edges.

    Notes
    -----
    The points are interpolated along the edges with a maximum distance of `segment`.
    """
    edge_points = []
    edge_indices = []
    # iterate over street_id, geometry
    for idx, geometry in edges["geometry"].items():
        if geometry.length < 2 * segment:
            # for edges that would result in no or one point, take the middle
            pts = [line_interpolate_point(geometry, 0.5, normalized=True)]
        else:
            # interpolate points along the line
            pts = line_interpolate_point(
                geometry,
                linspace(
                    0.1,
                    geometry.length - 0.1,
                    num=int((geometry.length - 0.1) // segment),
                ),
            )  # offset to keep nodes out
        edge_points.append(get_coordinates(pts))
        # get multi_indices of first row
        edge_indices += [idx] * len(pts)
    points = vstack(edge_points)
    return points, edge_indices


def reconstruct_edge_cells(voronoi_diagram, indices, crs):
    """Reconstruct edge cells from a Voronoi diagram.

    Regions with the hull index `-1` are discarded.

    Parameters
    ----------
    voronoi_diagram : scipy.spatial.Voronoi
        The Voronoi diagram to reconstruct.
    indices : list
        The indices of the points in the Voronoi diagram.
    crs : value
        The CRS used for the GeoDataFrame. Must be the same as the graph.
        Anything compatible with
        :meth:`pyproj.CRS.from_user_input() <pyproj.crs.CRS.from_user_input>`.

    Returns
    -------
    cells : geopandas.GeoDataFrame
        The Voronoi cells by their indices.
    """
    # Construct cell polygons for each of the dense points
    point_vertices = Series(voronoi_diagram.regions).take(voronoi_diagram.point_region)
    point_polygons = []
    for region in point_vertices:
        if -1 not in region:
            point_polygons.append(polygons(voronoi_diagram.vertices[region]))
        else:
            point_polygons.append(None)
    # Create GeoDataFrame with cells and edge multiindex
    poly_gdf = GeoDataFrame(
        geometry=point_polygons,
        crs=crs,
        index=indices,
        columns=["geometry"],
    )
    # Drop cells that are outside the boundary
    poly_gdf = poly_gdf.loc[poly_gdf.index != -1]
    # Dissolve cells by edge multiindex
    try:
        return poly_gdf.dissolve(by=poly_gdf.index)
    except GEOSException as err:  # pragma: no cover
        raise ValueError(
            "The tessellation might contain invalid geometries. "
            "Try increasing the segment length."
        ) from err


if __name__ == "__main__":
    main()
