from typing import Tuple, Iterable, Set, Tuple, Dict
from pyformlang.finite_automaton import EpsilonNFA
from networkx import MultiDiGraph
from scipy.sparse import dok_matrix, block_diag

from project.fa_building import build_minimal_dfa_by_regex, build_nfa_from_graph
from project.boolean_adjacency_matrix import BooleanAdjacencyMatrix


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


def find_accessible_vertices(
    regex: str,
    graph: MultiDiGraph,
    start_states: Set = None,
    final_states: Set = None,
    for_each: bool = False,
) -> Set:
    """
    Transforms the given graph and regular query into a deterministic state machine
    and finds accessible vertices in the graph based on the query
    """
    regex_nfa = build_minimal_dfa_by_regex(regex)
    graph_nfa = build_nfa_from_graph(graph, start_states, final_states)
    states = {ind: state for ind, state in enumerate(graph_nfa.states)}
    return find_accessible_by_matrices(
        BooleanAdjacencyMatrix(graph_nfa),
        BooleanAdjacencyMatrix(regex_nfa),
        states,
        for_each,
    )


def find_accessible_by_matrices(
    bd_matrix: BooleanAdjacencyMatrix,
    query_matrix: BooleanAdjacencyMatrix,
    states_dict: Dict,
    for_each: bool,
) -> Set[Tuple]:
    """
    Accessible function for regular queries to graph, represented as a BooleanAdjacencyMatrix.
    If for_each is false, then for the specified set of start states find a set of accessible ones.
    Otherwise, for each state from the specified set find a set of accessible vertices.
    """
    start_states = bd_matrix.start_states.nonzero()[1]
    final_states = set(bd_matrix.final_states.nonzero()[1])
    init_state_matrix, front = _initialize_state_matrices(
        bd_matrix, query_matrix, for_each
    )
    transitions = _create_transitions(query_matrix, bd_matrix)
    sum_fronts = _compute_sum_fronts(
        transitions, front, init_state_matrix, query_matrix.num_states
    )
    return _compute_result(
        bd_matrix,
        query_matrix,
        start_states,
        final_states,
        sum_fronts,
        states_dict,
        for_each,
    )


def _initialize_state_matrices(
    bd_matrix: BooleanAdjacencyMatrix,
    query_matrix: BooleanAdjacencyMatrix,
    for_each: bool,
) -> Tuple[dok_matrix, dok_matrix]:
    """
    The initial state matrix 'front' and an empty state matrix with the required size
    are initialized depending on how we find the accessible: for each separately or for all together.
    """
    bd_dok_start_states = bd_matrix.start_states
    bd_num_start_states = bd_dok_start_states.nnz

    q_num_states = query_matrix.num_states
    matrix_shape = (
        q_num_states * (bd_num_start_states if for_each else 1),
        bd_matrix.num_states + q_num_states,
    )
    init_state_matrix = dok_matrix(matrix_shape, dtype=bool)
    front = init_state_matrix.copy()
    if for_each:
        bd_start_states = bd_dok_start_states.nonzero()[1]
        for i in range(bd_num_start_states):
            for j in query_matrix.start_states.nonzero()[1]:
                index = j + query_matrix.num_states * i
                front[index, j] = True
                front[index, q_num_states + bd_start_states[i]] = True
    else:
        for i in query_matrix.start_states.nonzero()[1]:
            front[i, i] = True
            front[i, q_num_states:] = bd_dok_start_states

    return init_state_matrix, front


def _create_transitions(
    query_matrix: BooleanAdjacencyMatrix, bd_matrix: BooleanAdjacencyMatrix
) -> Dict[str, dok_matrix]:
    """
    Create a transition diagonal matrix, where each block corresponds
    to a label that is present in both boolean adjacency matrices 'bd_matrix'
    and 'query_matrix'.
    """
    m_bd = bd_matrix.adj_matrices
    m_q = query_matrix.adj_matrices
    common_labels = m_bd.keys() & m_q.keys()

    transition = {}
    for i in common_labels:
        transition[i] = block_diag((m_q[i], m_bd[i]))

    return transition


def _compute_sum_fronts(
    transitions: Dict[str, dok_matrix],
    front: dok_matrix,
    init_state_matrix: dok_matrix,
    q_num_states: int,
) -> dok_matrix:
    """
    Actually bfs algorithm. We pass along each front and find accessible states
    """
    prev_nnz = None
    sum_fronts = init_state_matrix.copy()
    while prev_nnz != sum_fronts.nnz:
        prev_nnz = sum_fronts.nnz
        new_front = init_state_matrix.copy()
        for v in transitions.values():
            all_state = front * v
            q_state = all_state[0:, 0:q_num_states]
            bd_state = all_state[0:, q_num_states:]
            for k, t in zip(*q_state.nonzero()):
                n = q_num_states * (k // q_num_states) + t
                new_front[n, t % q_num_states] = True
                new_front[n, q_num_states:] += bd_state[k]
        front = new_front
        sum_fronts += front

    return sum_fronts


def _compute_result(
    bd_matrix: BooleanAdjacencyMatrix,
    query_matrix: BooleanAdjacencyMatrix,
    start_states: dok_matrix,
    final_states: Set,
    sum_fronts: dok_matrix,
    states_dict: Dict,
    for_each: bool,
) -> Set:
    """
    Checks the received final sum_states of bfs with the final states of the query
    and generates the response as a set with reachable vertices.
    If for_each is true, then a response of reachable vertices for each vertex from the start_states is formed.
    """
    bd_num_start_states = bd_matrix.start_states.nnz
    q_num_states = query_matrix.num_states
    if for_each:
        res_matrix = dok_matrix((bd_num_start_states, bd_matrix.num_states), dtype=bool)
        for i in range(bd_num_start_states):
            for j in query_matrix.final_states.nonzero()[1]:
                index = j + q_num_states * i
                if sum_fronts[index, j]:
                    res_matrix[i] += sum_fronts[index, q_num_states:]
        result = {}
        for start, final in zip(*res_matrix.nonzero()):
            if final in final_states:
                key = states_dict[start_states[start]]
                value = states_dict[final]
                if key not in result:
                    result[key] = set()
                result[key].add(value)
    else:
        res_matrix = dok_matrix((1, bd_matrix.num_states), dtype=bool)
        for i in query_matrix.final_states.nonzero()[1]:
            if sum_fronts[i, i]:
                res_matrix += sum_fronts[i, q_num_states:]
        result = {states_dict[i] for i in res_matrix.nonzero()[1] if i in final_states}
    return result
