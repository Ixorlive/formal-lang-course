from collections import defaultdict, deque
from itertools import product
from typing import Tuple, NamedTuple, Set, Union, Iterable, Any

import networkx.drawing.nx_pydot
from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Terminal, Variable
import cfpq_data

from project.cfg_utils import to_weak_cfg, cfg_from_text, cfg_from_file


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


def get_cnf(cfg: CFG) -> CFG:
    weak_cfg = to_weak_cfg(cfg)
    return weak_cfg.to_normal_form()


def hellings_algorithm(cfg: CFG, graph: MultiDiGraph) -> Set[Tuple[str, str, str]]:
    """
    Computes the reachability information for all pairs of vertices in the given graph and context-free grammar.

    Args:
        cfg(CFG): The context-free grammar (CFG) to use for reachability analysis.
        graph(MultiDiGraph): The directed graph on which to perform reachability analysis.

    Returns:
        Set[Tuple[int, Variable, int]]: A set of triples (start_vertex, nonterminal, end_vertex)
        representing the reachability information for all pairs of vertices in the graph.
    """
    if graph.number_of_nodes() == 0:
        return set()

    wcnf = to_weak_cfg(cfg)
    term_to_nonterm = defaultdict(set)
    nonterm_pair_to_nonterm = defaultdict(set)
    epsilon_nonterms = set()
    for prod in wcnf.productions:
        head, body = prod.head, prod.body
        body_len = len(body)
        if body_len == 0:
            epsilon_nonterms.add(head)
        elif body_len == 1:
            term_to_nonterm[head].add(body[0])
        elif body_len == 2:
            nonterm_pair_to_nonterm[head].add((body[0], body[1]))

    result = {(node, var, node) for node in graph.nodes for var in epsilon_nonterms}
    result.update(
        (i, n, j)
        for i, j, label in graph.edges(data="label")
        for n, terms in term_to_nonterm.items()
        if Terminal(label) in terms
    )

    while True:
        new_result = result.copy()
        for i, j, k in product(graph.nodes, repeat=3):
            for var1, pairs in nonterm_pair_to_nonterm.items():
                for var2, var3 in pairs:
                    if (i, var2, j) in result and (j, var3, k) in result:
                        new = (i, var1, k)
                        if new not in result:
                            new_result.add(new)
        if new_result == result:
            break
        result = new_result

    return result


def reachability_with_nonterminal(
    grammar: CFG,
    graph: MultiDiGraph,
    start_vertices: Set,
    end_vertices: Set,
    target_nonterminal: Variable,
) -> Set[Tuple[int, int]]:
    """
    Computes the reachability information for the specified start and end vertices
    and the given nonterminal in the context-free grammar.

    Args:
        grammar(CFG): The context-free grammar (CFG) to use for reachability analysis.
        graph(MultiDiGraph): The directed graph on which to perform reachability analysis.
        start_vertices(Set[int]): A set of start vertices for which to compute reachability.
        end_vertices(Set[int]): A set of end vertices for which to compute reachability.
        target_nonterminal(Variable): The nonterminal to consider for reachability analysis.

    Returns:
        Set[Tuple[int, int]]: A set of pairs (start_vertex, end_vertex) representing the reachability
        information for the specified start and end vertices and the given nonterminal in the CFG.
    """
    reachability = hellings_algorithm(grammar, graph)

    filtered_reachability = {
        (src, dest)
        for src, nonterm, dest in reachability
        if nonterm == target_nonterminal
        and src in start_vertices
        and dest in end_vertices
    }

    return filtered_reachability
