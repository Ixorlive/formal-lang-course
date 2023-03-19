import pytest
from typing import List

from project.reg_querying import *


@pytest.mark.parametrize(
    "regexes",
    [
        ["abc", "bca", "aaa"],
        ["ab*c", "ba*c*", "c*a*s*f", "aa*bb*cc*d"],
        ["abc | cda", "cda | ads", "a | b | c", "aaa | bbb"],
        ["abc", "abc*d", "a*b*c*", "a | b", "abc | bca", "bca", "a*bc | bc*a"],
    ],
)
def test_intersect(regexes: List[str]):
    fas = [build_minimal_dfa_by_regex(regex) for regex in regexes]
    for fa1 in fas:
        for fa2 in fas:
            expected = fa1.get_intersection(fa2)
            actual = intersect(fa1, fa2)
            assert expected.is_equivalent_to(actual)


@pytest.fixture
def graph() -> MultiDiGraph:
    g = MultiDiGraph()
    g.add_edge(0, 1, label="a")
    g.add_edge(0, 2, label="b")
    g.add_edge(1, 3, label="c")
    g.add_edge(2, 3, label="d")
    g.add_edge(3, 4, label="e")
    return g


@pytest.fixture
def graph_2() -> MultiDiGraph:
    graph = MultiDiGraph()
    graph.add_edges_from(
        [
            ("A", "B", {"label": "x"}),
            ("A", "C", {"label": "y"}),
            ("B", "C", {"label": "z"}),
            ("B", "D", {"label": "x"}),
            ("C", "E", {"label": "y"}),
            ("D", "C", {"label": "z"}),
            ("D", "E", {"label": "y"}),
            ("E", "A", {"label": "x"}),
        ]
    )
    return graph


def test_regular_query(graph: MultiDiGraph):
    regex = "a*(b|c)*e"
    start_states = [0]
    final_states = [4]

    result = regular_query(regex, graph, start_states, final_states)
    expected = {(0, 4)}

    assert result == expected

    # Test with no start_states and final_states
    result = regular_query(regex, graph)
    expected = {(0, 4), (3, 4), (1, 4)}

    assert result == expected

    # Test with empty result
    regex = "a(b|c)+e"
    result = regular_query(regex, graph, start_states, final_states)
    expected = set()

    assert result == expected


def test_accessible_query_for_any(graph_2: MultiDiGraph):
    # Test for_any=True with specified start state
    start_states = {"A"}
    result = find_accessible_vertices("(x|y)", graph_2, start_states)
    assert result == {"B", "C"}

    # Test for_any=True with empty start state
    result = find_accessible_vertices("x|y", graph_2, None)
    assert result == {"A", "B", "C", "D", "E"}

    # Test for_any=True with unreachable start state
    start_states = {"X"}
    result = find_accessible_vertices("x|y", graph_2, start_states)
    assert result == set()

    # Test for_any=True with final state
    start_states = {"A"}
    final_states = {"C"}
    result = find_accessible_vertices("x|y", graph_2, start_states, final_states)
    assert result == {"C"}

    # Test for_any=True with unreachable final state
    start_states = {"A"}
    final_states = {"X"}
    result = find_accessible_vertices("x|y", graph_2, start_states, final_states)
    assert result == set()


def test_accessible_query_for_any_2(graph_2: MultiDiGraph):
    start_states = {"A"}
    result = find_accessible_vertices("(x|y) x*", graph_2, start_states)
    assert result == {"B", "C", "D"}

    start_states = {"A"}
    result = find_accessible_vertices("(x|y)*", graph_2, start_states)
    assert result == {"B", "C", "D", "E", "A"}

    start_states = {"A"}
    result = find_accessible_vertices("x z y", graph_2, start_states)
    assert result == {"E"}

    start_states = {"A", "B"}
    result = find_accessible_vertices("z", graph_2, start_states)
    assert result == {"C"}


def test_accessible_query_for_first_graph(graph: MultiDiGraph):
    regex = "a*(b|c)*e"
    result = find_accessible_vertices(regex, graph, {0})
    assert result == {4}
    result = find_accessible_vertices(regex, graph, {2})
    assert result == set()
    result = find_accessible_vertices(regex, graph, {0, 2}, for_each=True)
    assert result == {0: {4}}


def test_accessible_query_for_each(graph_2: MultiDiGraph):
    start_states = {"A", "C"}
    result = find_accessible_vertices("(x|y)", graph_2, start_states, for_each=True)
    assert result == {"A": {"C", "B"}, "C": {"E"}}

    result = find_accessible_vertices("x|y", graph_2, None, for_each=True)
    assert result == {"C": {"E"}, "E": {"A"}, "A": {"C", "B"}, "D": {"E"}, "B": {"D"}}

    start_states = {"A", "D"}
    result = find_accessible_vertices("y*x", graph_2, start_states, for_each=True)
    assert result == {"D": {"A"}, "A": {"B", "A"}}

    start_states = {"A", "B", "C", "D"}
    result = find_accessible_vertices("(x|y)*", graph_2, start_states, for_each=True)
    assert result == {
        "A": {"D", "E", "C", "A", "B"},
        "D": {"D", "E", "C", "A", "B"},
        "C": {"D", "E", "C", "A", "B"},
        "B": {"D", "E", "C", "A", "B"},
    }

    start_states = {"A", "B", "C", "D"}
    result = find_accessible_vertices("(x|z)*", graph_2, start_states, for_each=True)
    assert result == {"A": {"D", "C", "B"}, "D": {"C"}, "B": {"D", "C"}}
