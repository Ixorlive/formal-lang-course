import os
from textwrap import dedent

from project.graph_utils import *


def test_get_graph_info_by_name():
    stats = get_graph_info_by_name("skos")
    assert stats.number_of_nodes == 144
    assert stats.number_of_edges == 252
    assert stats.edge_labels == {'isDefinedBy', 'range', 'definition', 'inverseOf', 'creator', 'unionOf', 'subClassOf',
                                 'label', 'seeAlso', 'contributor', 'title', 'disjointWith', 'rest', 'comment', 'first',
                                 'domain', 'scopeNote', 'description', 'type', 'subPropertyOf', 'example'}


def test_create_labeled_two_cycles_graph():
    n = 3
    m = 3
    labels = ('x', 'y')
    graph = create_labeled_two_cycles_graph(n, m, labels)
    graph_info = get_graph_info(graph)
    assert graph_info == GraphInfo(
        number_of_nodes=7,
        number_of_edges=8,
        edge_labels={'y', 'x'},
    )


def test_create_and_save_labeled_two_cycles_graph():
    n = 5
    m = 5
    labels = ('x', 'y')
    path = 'test_two_cycles.dot'
    create_and_save_labeled_two_cycles_graph(n, m, labels, path)
    assert os.path.exists(path)
    with open(path) as file:
        contents = "".join(file.readlines())
        expected = """\
            digraph  {
            1;
            2;
            3;
            4;
            5;
            0;
            6;
            7;
            8;
            9;
            10;
            1 -> 2  [key=0, label=x];
            2 -> 3  [key=0, label=x];
            3 -> 4  [key=0, label=x];
            4 -> 5  [key=0, label=x];
            5 -> 0  [key=0, label=x];
            0 -> 1  [key=0, label=x];
            0 -> 6  [key=0, label=y];
            6 -> 7  [key=0, label=y];
            7 -> 8  [key=0, label=y];
            8 -> 9  [key=0, label=y];
            9 -> 10  [key=0, label=y];
            10 -> 0  [key=0, label=y];
            }
            """
        expected = dedent(expected)
        contents = dedent(contents)
        assert expected == contents
    os.remove(path)
