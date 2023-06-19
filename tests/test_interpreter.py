import pytest

from project.interpreter import execute_string_and_return_result


@pytest.mark.parametrize(
    "input_str,output_str",
    [
        ("print(1);", "1\n"),
        ("print(1 in {1,2});", "True\n"),
        ("print(0 in {1,2});", "False\n"),
        ("print({1,2});", "{1, 2}\n"),
        ("x = 5; print(x);", "5\n"),
        ("x = 10; print(x in {0,1,2,10});", "True\n"),
        ("x = filter(x => x in {1..4}, {0..100}); print(x);", "{1, 2, 3, 4}\n"),
        ('q = map((x1,x2,x3) => x1, {{0, "asd", 1}}); print(q);', "{0}\n"),
        (
            """
                g = lift("abc");
                print(get_edges(g));
                """,
            "{(0, abc, 1)}\n",
        ),
        (
            """
                g = lift("abc");
                print(get_nodes(g));
                """,
            "{0, 1}\n",
        ),
        (
            """
                g = lift("abc");
                print(get_reachable(g));
                """,
            "{(0, 1)}\n",
        ),
    ],
)
def test_execute_string_and_return_result_basic(input_str, output_str):
    assert execute_string_and_return_result(input_str) == output_str


@pytest.mark.parametrize(
    "input_str,output_str",
    [
        (
            """
                l1 = lift("abc");
                l2 = lift("bca");
                res = l1 & l2;
                print(get_edges(res));
                print(get_nodes(res));
                print(get_labels(res));
                """,
            "{}\n{0, 3}\n{}\n",
        ),
        (
            """
                l1 = lift("abc");
                l2 = lift("bca");
                res = l1 | l2;
                print(get_nodes(res));
                """,
            "{(1, 0), (1, 1), (2, 0), (2, 1)}\n",
        ),
        (
            """
                l1 = lift("abc");
                l2 = lift("bca");
                res = l1 . l2;
                print(get_nodes(res));
                """,
            "{(1, 0), (1, 1), (2, 0), (2, 1)}\n",
        ),
    ],
)
def test_execute_string_and_return_result_basic_operation(input_str, output_str):
    assert execute_string_and_return_result(input_str) == output_str


@pytest.mark.parametrize(
    "dot_filename,expected_output",
    [
        ("tests/dot_graphs/simple_graph.dot", {"{('0', abc, '1')}\n"}),
        (
            "tests/dot_graphs/simple_graph2.dot",
            {
                "{('2', c, '0'), ('0', a, '1'), ('1', b, '2')}\n",
                "{('1', b, '2'), ('2', c, '0'), ('0', a, '1')}\n",
                "{('0', a, '1'), ('1', b, '2'), ('2', c, '0')}\n",
                "{('2', c, '0'), ('1', b, '2'), ('0', a, '1')}\n",
                "{('1', b, '2'), ('0', a, '1'), ('2', c, '0')}\n"
                "{('0', a, '1'), ('2', b, '0'), ('1', b, '2')}\n",
            },
        ),
    ],
)
def test_load_from_dot_file(dot_filename, expected_output):
    input_str = f"""
    g = load(\"{dot_filename}\");
    print(get_edges(g));
    """
    assert execute_string_and_return_result(input_str) in expected_output


@pytest.mark.parametrize(
    "dot_filename,expected_output",
    [
        ("tests/dot_graphs/simple_graph.dot", {0, 1, 3}),
        ("tests/dot_graphs/simple_graph2.dot", {0, 1, 2, 3}),
    ],
)
def test_add_set_states(dot_filename, expected_output):
    input_str = f"""
    g = load(\"{dot_filename}\");
    g = add_start(g, {{3}});
    print(get_start(g));
    """
    result = eval(execute_string_and_return_result(input_str))
    assert result == expected_output

    input_str = f"""
    g = load(\"{dot_filename}\");
    g = add_final(g, {{3}});
    print(get_final(g));
    """
    result = eval(execute_string_and_return_result(input_str))
    assert result == expected_output

    input_str = f"""
    g = load(\"{dot_filename}\");
    g = set_start(g, {{0}});
    print(get_start(g));
    """
    result = eval(execute_string_and_return_result(input_str))
    assert result == {0}

    input_str = f"""
    g = load(\"{dot_filename}\");
    g = set_final(g, {{1}});
    print(get_final(g));
    """
    result = eval(execute_string_and_return_result(input_str))
    assert result == {1}
