from typing import Tuple, Iterable
from pyformlang.finite_automaton import EpsilonNFA
from project.fa_building import build_minimal_dfa_by_regex, build_nfa_from_graph
from project.boolean_adjacency_matrix import BooleanAdjacencyMatrix
from networkx import MultiDiGraph


def intersect(fa1: EpsilonNFA, fa2: EpsilonNFA) -> EpsilonNFA:
    """
    Build intersection of two finite automatons using BooleanAdjacencyMatrix

    Args:
        fa1 (EpsilonNFA): The first epsilon-NFA.
        fa2 (EpsilonNFA): The second epsilon-NFA.

    Returns:
        EpsilonNFA: The epsilon-NFA resulting from the intersection of fa1 and fa2.
    """
    fa1_matrix = BooleanAdjacencyMatrix(fa1)
    fa2_matrix = BooleanAdjacencyMatrix(fa2)
    return fa1_matrix.get_intersection(fa2_matrix).to_nfa()


def regular_query(
    regex: str,
    graph: MultiDiGraph,
    start_states: Iterable[any] = None,
    final_stated: Iterable[any] = None,
) -> Iterable[Tuple[any, any]]:
    """
    Query finite automaton built out of a graph with a regular expression.

    Args:
        regex (str): The regular expression to be queried.
        graph (MultiDiGraph): The graph to convert to NFA.
        start_states (Iterable[any], optional): The starting states of the graph.
            If not specified, all nodes are assumed to be starting nodes. Defaults to None.
        final_stated (Iterable[any], optional): The final states of the graph.
            If not specified, all nodes are assumed to be final nodes. Defaults to None.

    Returns:
        Iterable[Tuple[any, any]]: Set of pairs (tuples) of graph nodes so that the second node
        is achievable from the first by a path that is accepted by
        the regular expression.
    """
    regex_graph_matrix = BooleanAdjacencyMatrix(build_minimal_dfa_by_regex(regex))
    graph_matrix = BooleanAdjacencyMatrix(
        build_nfa_from_graph(graph, start_states, final_stated)
    )

    intersected_matrix = graph_matrix.get_intersection(regex_graph_matrix)
    tc = intersected_matrix.get_transitive_closure()

    start_states_arr = intersected_matrix.start_states.toarray()
    final_states_arr = intersected_matrix.final_states.toarray()

    result = set()
    for start, final in zip(*tc.nonzero()):
        if start_states_arr[0, start] and final_states_arr[0, final]:
            start_v = start // regex_graph_matrix.num_states
            final_v = final // regex_graph_matrix.num_states
            result.add((start_v, final_v))
    return result
