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

    def get_states(self):
        result = set()
        for var, dfa in self.boxes.items():
            for x in dfa.states:
                result.add((var, x.value))
        return result

    def get_start_states(self):
        result = set()
        for var, dfa in self.boxes.items():
            if var not in self.start_symbol:
                continue
            for x in dfa.start_states:
                result.add((var, x))
        return result

    def get_final_states(self):
        result = set()
        for var, dfa in self.boxes.items():
            for x in dfa.final_states:
                result.add((var, x))
        return result

    def get_edges(self):
        result = set()
        for var, dfa in self.boxes.items():
            for fro, symb, to in dfa:
                result.add(((var, fro.value), symb.value, (var, to.value)))
        return result
