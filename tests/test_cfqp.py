import pytest
from pyformlang.cfg import CFG, Variable
from networkx import MultiDiGraph

from project.cfqp import hellings, matrix, reachability_with_nonterminal
from project.graph_utils import create_labeled_two_cycles_graph


@pytest.mark.parametrize("algo", [hellings, matrix])
def test_algorithms(algo):
    cfg_text = "S -> a S b | eps"
    cfg = CFG.from_text(cfg_text)
    graph = MultiDiGraph()
    graph.add_edges_from([(0, 1, {"label": "a"}), (1, 2, {"label": "b"})])

    result = algo(cfg, graph)

    expected_result = {(1, Variable("b#CNF#"), 2), (0, Variable("a#CNF#"), 1)}

    assert result == expected_result


@pytest.mark.parametrize("algo", ["hellings", "matrix"])
def test_reachability_with_nonterminal(algo: str):
    cfg_text = """
        S -> A B | B A
        A -> a A b | a b
        B -> b B a | b a
    """
    cfg = CFG.from_text(cfg_text)
    graph = MultiDiGraph()
    edges = [
        (0, 1, {"label": "a"}),
        (1, 2, {"label": "b"}),
        (2, 3, {"label": "b"}),
        (3, 4, {"label": "a"}),
        (0, 5, {"label": "b"}),
        (5, 6, {"label": "a"}),
        (6, 7, {"label": "a"}),
        (7, 8, {"label": "b"}),
    ]
    graph.add_edges_from(edges)

    start_vertices = graph.nodes
    end_vertices = graph.nodes
    target_nonterminal = Variable("S")

    result = reachability_with_nonterminal(
        cfg, graph, start_vertices, end_vertices, target_nonterminal, algo=algo
    )

    expected_result = {(0, 8), (0, 4)}
    assert expected_result == result


@pytest.mark.parametrize("algo", ["hellings", "matrix"])
def test_reachability_with_nonterminal2(algo: str):
    cfg_text = """
        S -> A B
        S -> A S1
        S1 -> S B
        A -> a
        B -> b
        """
    cfg = CFG.from_text(cfg_text)
    graph = create_labeled_two_cycles_graph(2, 1, labels=("a", "b"))

    start_vertices = graph.nodes
    end_vertices = graph.nodes
    target_nonterminal = Variable("S")

    result = reachability_with_nonterminal(
        cfg, graph, start_vertices, end_vertices, target_nonterminal, algo=algo
    )

    expected_result = {(0, 0), (0, 3), (1, 0), (1, 3), (2, 0), (2, 3)}
    assert len(expected_result) == len(result)
    for expected in expected_result:
        assert expected in result
