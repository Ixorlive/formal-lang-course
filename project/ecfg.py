from typing import AbstractSet, Dict, List
from pyformlang.cfg import Variable, CFG, Terminal
from pyformlang.regular_expression import Regex
from collections import defaultdict
from project.rfa import RFA


class ExtendedCFG:
    def __init__(
        self,
        variables: AbstractSet[Variable] = None,
        terminals: AbstractSet[Terminal] = None,
        start_symbol: Variable = None,
        productions: Dict[Variable, Regex] = None,
    ):
        self.variables = variables or set()
        self.terminals = terminals or set()
        self.start_symbol = start_symbol
        self.productions = productions or dict()

    def to_rfa(self) -> RFA:
        """
        Convert ExtendedCFG to RFA by converting each regular expression in the
        productions to its corresponding minimized epsilon NFA.

        Returns:
            An RFA instance created from the ExtendedCFG.
        """
        return RFA(
            start_symbol=self.start_symbol,
            boxes={
                h: b.to_epsilon_nfa().minimize() for h, b in self.productions.items()
            },
        )

    @staticmethod
    def from_cfg(cfg: CFG) -> "ExtendedCFG":
        """
        Convert a Context-Free Grammar (CFG) to an Extended Context-Free Grammar (ExtendedCFG).

        Args:
            cfg: A CFG object from the pyformlang library.

        Returns:
            An ExtendedCFG object that represents the given CFG.
        """
        production = defaultdict(list)

        for prod in cfg.productions:
            body_str = "".join(str(e.value) for e in prod.body) if prod.body else "$"
            production[prod.head].append(body_str)

        productions = {
            head: Regex(" | ".join(f"({elem})" for elem in body))
            for head, body in production.items()
        }

        return ExtendedCFG(
            variables=cfg.variables,
            terminals=cfg.terminals,
            start_symbol=cfg.start_symbol,
            productions=productions,
        )

    @staticmethod
    def from_text(text: str, start_symbol: Variable = Variable("S")) -> "ExtendedCFG":
        """
        Create an ExtendedCFG from a text string representing the grammar.

        Args:
            text: A string containing the grammar rules in the specified format.
            start_symbol: The start symbol for the grammar (default: Variable("S")).

        Returns:
            An ExtendedCFG instance created from the text input.
        """
        variables = set()
        productions: Dict[Variable, Regex] = dict()
        for line in text.splitlines():
            if not line.strip():
                continue
            prod = [str.strip(e) for e in line.split("->")]
            head, body = prod
            head = Variable(head)
            body = Regex(body)
            variables.add(head)
            productions[head] = body
        return ExtendedCFG(
            start_symbol=start_symbol, variables=variables, productions=productions
        )

    @staticmethod
    def from_file(path: str, start_symbol: Variable = Variable("S")) -> "ExtendedCFG":
        """
        Create an ExtendedCFG by reading the grammar from a file.

        Args:
            path: The path to the file containing the grammar rules in the specified format.
            start_symbol: The start symbol for the grammar (default: Variable("S")).

        Returns:
            An ExtendedCFG instance created from the grammar in the file.
        """
        with open(path) as file:
            return ExtendedCFG.from_text(file.read(), start_symbol=start_symbol)
