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
