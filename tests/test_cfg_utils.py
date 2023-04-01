import os
from pyformlang.cfg import CFG, Variable, Terminal, Production
from project.cfg_utils import *
import textwrap
import tempfile


def test_to_weak_cfg():
    weak_cfg = to_weak_cfg(cfg_from_text(
        textwrap.dedent(
            """
            S -> A A B
            A -> 0 A | A 0 | 1 A | A 1 | 1
            B -> 0 B | 1 B | epsilon 
            """)))
    expected = {
       Production(Variable("B"), [Variable("1#CNF#"), Variable("B")]),
       Production(Variable("B"), []),
       Production(Variable("C#CNF#1"), [Variable("A"), Variable("B")]),
       Production(Variable("A"), [Variable("0#CNF#"), Variable("A")]),
       Production(Variable("A"), [Variable("1#CNF#"), Variable("A")]),
       Production(Variable("A"), [Variable("A"), Variable("1#CNF#")]),
       Production(Variable("0#CNF#"), [Terminal("0")]),
       Production(Variable("B"), [Variable("0#CNF#"), Variable("B")]),
       Production(Variable("S"), [Variable("A"), Variable("C#CNF#1")]),
       Production(Variable("A"), [Terminal("1")]),
       Production(Variable("1#CNF#"), [Terminal("1")]),
       Production(Variable("A"), [Variable("A"), Variable("0#CNF#")])
    }
    assert weak_cfg.productions == expected


def test_wcfg_from_file():
    test_cfg = "S -> A B | B C | A | B\nA -> a\nB -> b\nC -> c"

    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir="./") as tmp_file:
        tmp_file.write(test_cfg)
        tmp_file.flush()
        tmp_filename = tmp_file.name

    weak_cfg = weak_cfg_from_file(tmp_filename)
    os.remove(tmp_filename)

    expected = {
        Production(Variable("S"), [Terminal("b")]),
        Production(Variable("S"), [Variable("B"), Variable("C")]),
        Production(Variable("S"), [Variable("A"), Variable("B")]),
        Production(Variable("B"), [Terminal("b")]),
        Production(Variable("A"), [Terminal("a")]),
        Production(Variable("S"), [Terminal("a")]),
        Production(Variable("C"), [Terminal("c")])
    }

    assert weak_cfg.productions == expected
