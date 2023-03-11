from typing import Tuple, Iterable
from pyformlang.finite_automaton import EpsilonNFA
from project.fa_building import build_minimal_dfa_by_regex, build_nfa_from_graph
from project.boolean_adjacency_matrix import BooleanAdjacencyMatrix
from networkx import MultiDiGraph


def intersect(fa1: EpsilonNFA, fa2: EpsilonNFA) -> EpsilonNFA:
    fa1_matrix = BooleanAdjacencyMatrix(fa1)
    fa2_matrix = BooleanAdjacencyMatrix(fa2)
    return fa1_matrix.get_intersection(fa2_matrix).to_nfa()


def regular_query(
    regex: str,
    graph: MultiDiGraph,
    start_states: Iterable[any] = None,
    final_stated: Iterable[any] = None,
) -> Iterable[Tuple[any, any]]:
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
