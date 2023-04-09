from project.ecfg import ExtendedCFG
from pyformlang.cfg import Variable, Production, Terminal, CFG
from pyformlang.regular_expression import Regex

# Test data
cfg_text = """
S -> aA | bB
A -> a | aA
B -> b | bB
"""


def test_from_text():
    cfg = ExtendedCFG.from_text(cfg_text)

    assert cfg.start_symbol == Variable("S")
    assert len(cfg.variables) == 3
    expected = {
        Variable("S"): Regex("aA|bB"),
        Variable("A"): Regex("a|aA"),
        Variable("B"): Regex("b|bB"),
    }
    for k, v in expected.items():
        assert k in cfg.productions
        assert str(v) == str(cfg.productions[k])


def test_to_rfa():
    cfg = ExtendedCFG.from_text(cfg_text)
    rfa = cfg.to_rfa()

    assert rfa.start_symbol == Variable("S")
    assert len(rfa.boxes) == 3

    for var, dfa in rfa.boxes.items():
        regex = cfg.productions[var]
        epsilon_nfa = regex.to_epsilon_nfa()
        minimized_nfa = epsilon_nfa.minimize()

        assert dfa.is_equivalent_to(minimized_nfa)


def test_from_file(tmp_path):
    cfg_file = tmp_path / "cfg.txt"
    cfg_file.write_text(cfg_text)

    cfg = ExtendedCFG.from_file(cfg_file)

    assert cfg.start_symbol == Variable("S")
    assert len(cfg.variables) == 3
    expected = {
        Variable("S"): Regex("aA|bB"),
        Variable("A"): Regex("a|aA"),
        Variable("B"): Regex("b|bB"),
    }
    for k, v in expected.items():
        assert k in cfg.productions
        assert str(v) == str(cfg.productions[k])


def test_from_cfg():
    cfg = ExtendedCFG.from_cfg(CFG.from_text(cfg_text))
    assert cfg.start_symbol == Variable("S")
    assert len(cfg.variables) == 3
    expected = {
        Variable("S"): Regex("aA|bB"),
        Variable("A"): Regex("a|aA"),
        Variable("B"): Regex("b|bB"),
    }
    for k, v in expected.items():
        assert cfg.productions[k].to_epsilon_nfa().is_equivalent_to(v.to_epsilon_nfa())
