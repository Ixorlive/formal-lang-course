from typing import Union, Set, Tuple
from collections import defaultdict
from itertools import product

import networkx.drawing.nx_pydot as nx_pydot
from pyformlang.cfg import CFG, Terminal, Variable
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix

from project.cfg_utils import to_weak_cfg, cfg_from_text


def hellings(cfg: Union[str, CFG], graph: MultiDiGraph) -> Set[Tuple]:
    """
    Computes the reachability information for all pairs of vertices in the given graph and context-free grammar.

    Args:
        cfg(CFG): The context-free grammar (CFG) to use for reachability analysis.
        graph(MultiDiGraph): The directed graph on which to perform reachability analysis.

    Returns:
        Set[Tuple[int, Variable, int]]: A set of triples (start_vertex, nonterminal, end_vertex)
        representing the reachability information for all pairs of vertices in the graph.
    """
    if isinstance(cfg, str):
        cfg = cfg_from_text(cfg)
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


def hellings_from_file(cfg: Union[str, CFG], path_to_graph: str) -> Set[Tuple]:
    """
    Runs the Hellings algorithm on a graph read from a file.

    The file should contain one edge per line, with each line formatted as "source_node target_node edge_label".

    Args:
        cfg: The context-free grammar to use for the algorithm, either as a string or as a CFG object.
        path_to_graph: The path to the file containing the graph.

    Returns:
        The set of all valid paths through the graph that match the grammar, as tuples of (start_node, end_node, label).
    """
    graph = MultiDiGraph()
    with open(path_to_graph, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                source_node, target_node, edge_label = line.split()
                graph.add_edge(int(source_node), int(target_node), label=edge_label)
    return hellings(cfg, graph)


def hellings_from_pydot(cfg: Union[str, CFG], dot_file: str) -> Set[Tuple]:
    return hellings(cfg, nx_pydot.from_pydot(dot_file))


def matrix(cfg: Union[str, CFG], graph: MultiDiGraph) -> Set[Tuple]:
    """
    Computes the reachability information for all pairs of vertices in the given graph and context-free grammar
    based on a matrix algorithm.

    Args:
        cfg(CFG): The context-free grammar (CFG) to use for reachability analysis.
        graph(MultiDiGraph): The directed graph on which to perform reachability analysis.

    Returns:
        Set[Tuple[int, Variable, int]]: A set of triples (start_vertex, nonterminal, end_vertex)
        representing the reachability information for all pairs of vertices in the graph.
    """
    if isinstance(cfg, str):
        cfg = cfg_from_text(cfg)
    if graph.number_of_nodes() == 0:
        return set()

    cfg = to_weak_cfg(cfg)
    node_to_idx = {v: i for i, v in enumerate(graph.nodes)}
    n = graph.number_of_nodes()
    T = {var: dok_matrix((n, n), dtype=bool) for var in cfg.variables}

    for production in cfg.productions:
        var = production.head
        if len(production.body) == 0:
            for i in range(n):
                T[var][i][i] = True
        elif len(production.body) == 1:
            terminal = production.body[0]
            for u, v, s in graph.edges.data(data="label"):
                if Variable(s) == terminal:
                    i, j = node_to_idx[u], node_to_idx[v]
                    T[var][i, j] = True

    while True:
        changed = False
        for production in cfg.productions:
            var = production.head
            if len(production.body) != 2:
                continue
            for var1 in T:
                for var2 in T:
                    if [var1, var2] != production.body:
                        continue

                    new_matrix = T[var] + T[var1] @ T[var2]
                    if not (new_matrix - T[var]).nnz == 0:
                        changed = True
                    T[var] = new_matrix

        if not changed:
            break

    result = set()
    nodes = list(graph.nodes)
    for var in cfg.variables:
        u, v = T[var].nonzero()
        for i in range(len(u)):
            result.add((nodes[u[i]], var, nodes[v[i]]))
    return result


def matrix_from_file(cfg: Union[str, CFG], path_to_graph: str) -> Set[Tuple]:
    graph = MultiDiGraph()
    with open(path_to_graph, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                source_node, target_node, edge_label = line.split()
                graph.add_edge(int(source_node), int(target_node), label=edge_label)
    return matrix(cfg, graph)


def matrix_from_pydot(cfg: Union[str, CFG], dot_file: str) -> Set[Tuple]:
    return matrix(cfg, nx_pydot.from_pydot(dot_file))


solver_algo_map = {"hellings": hellings, "matrix": matrix}


def reachability_with_nonterminal(
    grammar: Union[str, CFG],
    graph: MultiDiGraph,
    start_vertices: Set,
    end_vertices: Set,
    target_nonterminal: Variable,
    algo: str = "hellings",
) -> Set[Tuple[int, int]]:
    """
    Computes the reachability information for the specified start and end vertices
    and the given nonterminal in the context-free grammar.

    Args:
        algo: A method that solves the problem of reachability between all pairs of vertices
              for a given graph and a given context-free grammar
        grammar(CFG): The context-free grammar (CFG) to use for reachability analysis.
        graph(MultiDiGraph): The directed graph on which to perform reachability analysis.
        start_vertices(Set[int]): A set of start vertices for which to compute reachability.
        end_vertices(Set[int]): A set of end vertices for which to compute reachability.
        target_nonterminal(Variable): The nonterminal to consider for reachability analysis.

    Returns:
        Set[Tuple[int, int]]: A set of pairs (start_vertex, end_vertex) representing the reachability
        information for the specified start and end vertices and the given nonterminal in the CFG.
    """
    if isinstance(grammar, str):
        grammar = cfg_from_text(grammar)

    reachability = solver_algo_map[algo](grammar, graph)

    filtered_reachability = {
        (src, dest)
        for src, nonterm, dest in reachability
        if nonterm == target_nonterminal
        and src in start_vertices
        and dest in end_vertices
    }

    return filtered_reachability
