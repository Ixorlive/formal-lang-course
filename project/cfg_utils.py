from pyformlang.cfg import CFG, Variable


def to_weak_cfg(cfg: CFG) -> CFG:
    grammar = cfg.eliminate_unit_productions().remove_useless_symbols()
    grammar_prod = grammar._get_productions_with_only_single_terminals()
    return CFG(
        start_symbol=grammar.start_symbol, productions=set(grammar._decompose_productions(grammar_prod))
    )


def cfg_from_text(text: str, start_symbol: Variable = Variable("S")) -> CFG:
    return CFG.from_text(text, start_symbol=start_symbol)


def cfg_from_file(path: str, start_symbol: Variable = Variable("S")) -> CFG:
    with open(path) as file:
        return cfg_from_text(file.read(), start_symbol)


def weak_cfg_from_file(path: str) -> CFG:
    return to_weak_cfg(cfg_from_file(path))
