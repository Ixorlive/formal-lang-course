import pytest

from project.parser import *

example_code = """
// Program start
gg = load("graph1.dot");
gg2 = load("graph2.dot");

intermediate = set_start(set_final(gg2, get_nodes(gg)), {1,2,3,4,5});

l1 = "type1" | "type2";
q1 = ("meta" | l1)*;
q2 = "subclass" . l1;

result1 = intermediate & q1;
result2 = intermediate & q2;

print(result1);

start_nodes = get_start(gg);

vertices_result1 = filter((node) => node in start_nodes, map((edge) => edge[0][0], get_edges(result1)));
vertices_result2 = filter((node) => node in start_nodes, map((edge) => edge[0][0], get_edges(result2)));

final_vertices = vertices_result1 & vertices_result2;

print(final_vertices);
// Program end
"""


def test_parse_string():
    parsed = parse_string("a = 1;")
    assert parsed is not None
    parsed = parse_string("a = start(b, c);")
    assert parsed is not None


@pytest.mark.parametrize(
    "input_string,expected",
    [
        ("a = 1;", True),
        ("a = set_start(b, c);", True),
        ("a = qwer;", True),
        ("a = 1;", True),
        (example_code, True),
        # compound operations
        ("a = b & c;", True),
        ("a = b . c;", True),
        ("a = b | c;", True),
        ("a = b *;", True),
        ("a = b in c;", True),
        ("a = b[5];", True),
        # set/list operations
        ("a = {1, 2, 3};", True),
        # lambda operations
        ("a = map((x) => x, {1,2,3});", True),
        ("a = map((b) => x in a, gg);", True),
        ("a = filter((x) => x in b, set_start(g,{1,23}));", True),
        ("a = set_start(", False),
        ("a = set_start(a);", False),
        ('a = load(("a");', False),
        ("a == set_start(b c);", False),
        ("a = set_start(b, ;", False),
        ("a = {1, 2, ;", False),
        ("a = [1, 2, ;", False),
        ("a = map((x) => x * 2, [1, 2, ;", False),
        ("a = filter((x) => x > 2, [1, 2, ;", False),
    ],
)
def test_check_correction_string(input_string, expected):
    assert check_correction_string(input_string) is expected


def test_generate_dot_text_with_valid_string():
    input_string = "var = set_start(s1, s2);"
    expected_output = """digraph {
0 [label="program"]
1 [label="stmt"]
0 -> 1
2 [label="bind"]
1 -> 2
3 [label="var: var"]
2 -> 3
4 [label="var: s1"]
5 [label="var: s2"]
}"""
    output = generate_dot_text(input_string)
    assert output == expected_output


def test_generate_dot_text_with_invalid_string():
    input_string = "a = start((a,b);"
    with pytest.raises(ParseCancellationException):
        generate_dot_text(input_string)
