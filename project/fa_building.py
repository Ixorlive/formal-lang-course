import networkx as nx
from typing import Collection, Optional
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
)
from pyformlang.regular_expression import Regex


def build_minimal_dfa_by_regex(regex: str) -> DeterministicFiniteAutomaton:
    """
    Builds a minimal deterministic finite automaton (DFA)
    that recognizes the language specified by the given regular expression.

    Args:
        regex: a string representing the regular expression to build the DFA from

    Returns:
        A DeterministicFiniteAutomaton object representing the minimal DFA
        that recognizes the language specified by the regular expression.
    """
    reg_expr = Regex(regex)
    nfa = reg_expr.to_epsilon_nfa()
    minimal_dfa = nfa.minimize()
    return minimal_dfa


def build_nfa_from_graph(
    graph: nx.MultiDiGraph,
    start: Optional[Collection] = None,
    end: Optional[Collection] = None,
) -> NondeterministicFiniteAutomaton:
    """
    Builds a non-deterministic finite automaton (NFA)
        that recognizes the language corresponding to the specified graph.

    Args:
    - graph: a networkx Graph object representing the graph to build the NFA from
    - start: a list of vertices to use as starting states of the NFA
        (if None, consider all vertices as starting states)
    - end: a list of vertices to use as accepting states of the NFA
        (if None, consider all vertices as accepting states)

    Returns:
    A NondeterministicFiniteAutomaton object representing the NFA
        that recognizes the language corresponding to the specified graph.
    """
    nfa = NondeterministicFiniteAutomaton()

    all_nodes = set(graph.nodes)
    if start is None:
        start = all_nodes
    if end is None:
        end = all_nodes

    for node in start:
        nfa.add_start_state(node)
    for node in end:
        nfa.add_final_state(node)

    for node_from, node_to, label in graph.edges(data="label"):
        nfa.add_transition(node_from, label, node_to)

    return nfa
