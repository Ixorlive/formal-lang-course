from typing import NamedTuple, Dict
from pyformlang.cfg import Variable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton


class RFA(NamedTuple):
    start_symbol: Variable
    boxes: Dict[Variable, DeterministicFiniteAutomaton]

    def minimize(self):
        """
        Minimize the DFAs within the RFA.

        Returns:
            A new RFA instance with minimized DFAs for each variable.
        """
        return RFA(
            start_symbol=self.start_symbol,
            boxes={var: dfa.minimize() for var, dfa in self.boxes.items()},
        )
