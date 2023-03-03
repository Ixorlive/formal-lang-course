from project.fa_building import *
from project.graph_utils import create_labeled_two_cycles_graph

from networkx import MultiDiGraph
import pyformlang.finite_automaton as fa


def test_build_minimal_dfa_by_regex_2():
    # Test with regex "a*b*"
    regex = "a*b*"
    actual_dfa = build_minimal_dfa_by_regex(regex)

    # Build the expected DFA
    expected_dfa = DeterministicFiniteAutomaton()

    state_1 = fa.State(0)
    state_2 = fa.State(1)
    symbol_1 = fa.Symbol("a")
    symbol_2 = fa.Symbol("b")

    expected_dfa.add_start_state(state_1)
    expected_dfa.add_final_state(state_1)
    expected_dfa.add_final_state(state_2)

    expected_dfa.add_transition(state_1, symbol_1, state_1)
    expected_dfa.add_transition(state_2, symbol_2, state_2)
    expected_dfa.add_transition(state_1, symbol_2, state_2)

    # Assert that the actual DFA is equivalent to the expected DFA
    assert expected_dfa.is_equivalent_to(actual_dfa)


def test_build_minimal_dfa_by_regex():
    regex = "a (b|c)* d"
    dfa = build_minimal_dfa_by_regex(regex)

    # Check that the DFA recognizes the correct language
    assert dfa.accepts("abd")
    assert dfa.accepts("acd")
    assert not dfa.accepts("abc")

    # Check that the DFA has the correct start state
    assert dfa.start_state == fa.State("0")
    assert dfa.final_states == {fa.State("1")}


def test_build_minimal_dfa_by_regex_minimal():
    regex = "a (b|c)* d"
    dfa = build_minimal_dfa_by_regex(regex)

    # Check that the minimal DFA has the same language as the non-minimal DFA
    non_minimal_dfa = Regex(regex).to_epsilon_nfa().to_deterministic()
    assert dfa.is_equivalent_to(non_minimal_dfa)

    # Check that the minimal DFA has the correct number of states
    expected_num_states = 3
    assert len(dfa.states) == expected_num_states

    # Check that the minimal DFA has the correct number of transitions
    expected_num_transitions = 4
    assert dfa.get_number_transitions() == expected_num_transitions


def test_build_nfa_from_graph_simple():
    # Test graph with start and end states
    g1 = nx.MultiDiGraph()
    g1.add_edges_from([(0, 1, {"label": "a"}), (1, 2, {"label": "b"})])
    expected1 = NondeterministicFiniteAutomaton()
    expected1.add_transition(0, "a", 1)
    expected1.add_transition(1, "b", 2)
    expected1.add_start_state(0)
    expected1.add_final_state(2)
    assert expected1.is_equivalent_to(build_nfa_from_graph(g1, start={0}, end={2}))

    # Test graph with all states as start and end
    g2 = nx.MultiDiGraph()
    g2.add_edges_from([(0, 1, {"label": "a"}), (1, 2, {"label": "b"})])
    expected2 = NondeterministicFiniteAutomaton()
    expected2.add_transition(0, "a", 1)
    expected2.add_transition(1, "b", 2)
    expected2.add_start_state(0)
    expected2.add_start_state(1)
    expected2.add_start_state(2)
    expected2.add_final_state(0)
    expected2.add_final_state(1)
    expected2.add_final_state(2)
    assert expected2.is_equivalent_to(build_nfa_from_graph(g2))


def test_build_nfa_from_graph_two_cycled():
    graph = create_labeled_two_cycles_graph(5, 5, ("a", "b"))
    assert not build_nfa_from_graph(graph).is_deterministic()


def test_build_nfa_from_graph_empty():
    assert build_nfa_from_graph(MultiDiGraph()).is_empty()
