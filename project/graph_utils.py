from typing import Tuple, NamedTuple, Set, Union, Iterable, Any

import networkx.drawing.nx_pydot
from networkx import MultiDiGraph
import cfpq_data


class GraphInfo(NamedTuple):
    number_of_nodes: int
    number_of_edges: int
    edge_labels: Set[str]


def get_graph_info(graph: MultiDiGraph) -> GraphInfo:
    """
    Computes statistics about a MultiGraph object.

    Args:
        graph: A MultiGraph object.

    Returns:
        A GraphStats object containing the name, number of nodes, number of edges,
        and set of edge labels for the input graph.
    """
    edge_labels = set(
        label for _, _, label in graph.edges(data="label") if label
    )  # Extract non-empty edge labels

    return GraphInfo(graph.number_of_nodes(), graph.number_of_edges(), edge_labels)


def download_graph(graph_name: str) -> MultiDiGraph:
    """
    Downloads a graph with the given name from the cfpq_data library.

    Args:
        graph_name: The name of the graph to download.

    Returns:
        A MultiGraph object representing the downloaded graph.
    """
    path_to_graph = cfpq_data.download(graph_name)
    return cfpq_data.graph_from_csv(path_to_graph)


def get_graph_info_by_name(graph_name: str) -> GraphInfo:
    """
    Downloads a graph with the given name and returns statistics about it.

    Args:
        graph_name: The name of the graph to download.

    Returns:
        A GraphStats object containing the name, number of nodes, number of edges,
        and set of edge labels for the downloaded graph.
    """
    multi_graph = download_graph(graph_name)
    return get_graph_info(multi_graph)


def save_graph(graph: MultiDiGraph, path: str):
    """
    Saves the specified MultiGraph to a file in DOT format at the specified path.

    Args:
    - graph: the MultiGraph to save
    - path: the path to the file where the DOT representation of the graph will be saved
    """
    networkx.drawing.nx_pydot.write_dot(graph, path)


def create_labeled_two_cycles_graph(
    n: Union[int, Iterable[Any]], m: Union[int, Iterable[Any]], labels: Tuple[str, str]
) -> MultiDiGraph:
    """
    Creates a labeled two-cycle graph with the specified number of vertices and labels, and saves it to a file in DOT format at the specified path.

    Args:
    - n: the number of vertices in the first cycle
    - m: the number of vertices in the second cycle
    - labels: a tuple of two label names to use for the edges between the two cycles
    - path: the path to the file where the DOT representation of the graph will be saved
    """
    return cfpq_data.labeled_two_cycles_graph(n, m, labels=labels)


def create_and_save_labeled_two_cycles_graph(
    n: Union[int, Iterable[Any]],
    m: Union[int, Iterable[Any]],
    labels: Tuple[str, str],
    path: str,
):
    """
    calls Create_labeled_two_cycles_graph and saves the graph
    """
    created_graph = create_labeled_two_cycles_graph(n, m, labels)
    save_graph(created_graph, path)
