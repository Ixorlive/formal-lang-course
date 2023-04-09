import pytest
from project.ecfg import ExtendedCFG


def create_sample_rfa(rfa_text: str):
    cfg = ExtendedCFG.from_text(rfa_text)
    return cfg.to_rfa()


@pytest.mark.parametrize(
    "rfa_text",
    [
        "",
        """
                 S -> aA | bB
                 A -> a | aA
                 B -> b | bB
                 """,
        """
                 S -> (a) | (b* S)
                 """,
    ],
)
def test_rfa_minimize(rfa_text):
    rfa = create_sample_rfa(rfa_text)
    minimized_rfa = rfa.minimize()

    for var, dfa in minimized_rfa.boxes.items():
        minimized_dfa = dfa.minimize()
        assert dfa == minimized_dfa
