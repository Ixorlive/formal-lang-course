from dataclasses import dataclass
from pyformlang.finite_automaton import Symbol
from pyformlang.cfg import Variable
import networkx as nx

from project import RFA
from project.reg_querying import *
from project.antlr.LanguageParser import LanguageParser
from project.antlr.LanguageVisitor import LanguageVisitor


class TypingError(Exception):
    _what: str

    def __init__(self, what: str):
        self._what = what

    def __str__(self):
        return self._what


def add_result_to_set(result_set: set, element, transformed_element):
    result_set.add(transformed_element)


def add_element_if_condition_true(result_set: set, element, condition):
    if condition:
        result_set.add(element)


@dataclass
class WrapperRFA:
    nfa: EpsilonNFA


class ExecutorVisitor(LanguageVisitor):
    def __init__(self, writer):
        self.writer = writer
        self.environment = [{}]
        self.lambda_helper = None
        self.lambda_pars: Set = set()

    def build_rfa(self, rsm: WrapperRFA) -> RFA:
        variable_names = {
            symb.value.value
            for _, symb, _ in rsm.nfa
            if isinstance(symb.value, Variable)
        }
        automata_dict = {}
        for name in variable_names:
            if name not in self.environment[-1]:
                raise TypingError(f"Could not find name {name}")
            automaton = self.environment[-1][name]
            if not isinstance(automaton, (EpsilonNFA, WrapperRFA)):
                raise TypingError(f"{name} is {type(name)}, not Finite Automaton")
            automata_dict[name] = automaton.nfa
        return RFA({Variable("$")}, automata_dict)

    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.visitChildren(ctx)

    def visitExprLoad(self, ctx: LanguageParser.ExprLoadContext) -> EpsilonNFA:
        filename = self.visit(ctx.literalString())
        graph = nx.nx_pydot.read_dot(filename)
        nfa = build_nfa_from_graph(graph)
        return nfa

    """
        Bind, Print, Expr, Var
    """

    def visitBind(self, ctx: LanguageParser.BindContext):
        var_name = ctx.var().getText()
        value = self.visit(ctx.expr())
        self.environment[0][var_name] = value
        return value

    def visitPrint(self, ctx: LanguageParser.PrintContext):
        value = self.visit(ctx.expr())
        if isinstance(value, frozenset):
            print("{%s}" % ", ".join(map(str, value)), file=self.writer)
        else:
            print(value, file=self.writer)
        return value

    def visitExprExpr(self, ctx: LanguageParser.ExprExprContext):
        return self.visit(ctx.children[1])

    def visitVar(self, ctx: LanguageParser.VarContext) -> str:
        return str(ctx.children[0])

    def visitExprVar(self, ctx: LanguageParser.ExprVarContext):
        name = self.visit(ctx.children[0])
        if name in self.environment[-1]:
            return self.environment[-1][name]
        else:
            raise TypingError(f"No variable {name} found")

    """
        Literals
    """

    def visitLiteralInt(self, ctx: LanguageParser.LiteralIntContext):
        return int(ctx.INT().getText())

    def visitLiteralString(self, ctx: LanguageParser.LiteralStringContext):
        return ctx.STRING().getText()[1:-1]

    def visitExprSet(self, ctx: LanguageParser.ExprSetContext):
        return frozenset(self.visit(expr) for expr in ctx.expr())

    def visitSet(self, ctx: LanguageParser.SetContext):
        result = set()
        for child in ctx.children[1:-1:2]:
            val = self.visit(child)
            if isinstance(val, set):
                result.update(val)
            else:
                result.add(val)
        return frozenset(result)

    def visitSetElemRange(self, ctx: LanguageParser.SetElemRangeContext) -> Set:
        start = int(ctx.literalInt(0).getText())
        end = int(ctx.literalInt(1).getText())
        return {i for i in range(start, end + 1)}

    def visitLiteralRec(self, ctx: LanguageParser.LiteralRecContext) -> WrapperRFA:
        variable_name = self.visit(ctx.var())
        nfa = EpsilonNFA()
        nfa.add_start_state(State(0))
        nfa.add_final_state(State(1))
        nfa.add_transition(State(0), Variable(variable_name), State(1))
        return WrapperRFA(nfa)

    """
        Lambda, Map, Filtering, patterns for lambdas
    """

    def visitLambdaParens(self, ctx: LanguageParser.LambdaParensContext):
        return self.visit(ctx.children[1])

    def visitLambdaExpr(self, ctx: LanguageParser.LambdaExprContext):
        pattern_node = ctx.children[0]
        expr_node = ctx.children[2]
        current_env_copy = self.environment[-1].copy()
        self.environment.append(current_env_copy)
        result = set()
        for values in self.lambda_pars:
            self._evaluate_expression_for_param(expr_node, pattern_node, result, values)
        self.environment.pop()
        return frozenset(result)

    def _evaluate_expression_for_param(self, expr_node, pattern_node, result, values):
        patterns = self.visit(pattern_node)
        if isinstance(patterns, list):
            for pattern, value in zip(patterns, values):
                self.environment[-1][pattern] = value
        else:
            self.environment[-1][patterns] = values
        fx = self.visit(expr_node)
        self.lambda_helper(result, values, fx)

    def visitPatternVar(self, ctx: LanguageParser.PatternVarContext):
        return ctx.var().getText()

    def visitPatternTuple(self, ctx: LanguageParser.PatternTupleContext):
        return [self.visit(p) for p in ctx.pattern()]

    def visitExprMap(self, ctx: LanguageParser.ExprMapContext):
        pars = self.visit(ctx.children[4])
        if not isinstance(pars, frozenset):
            raise TypingError(f"{type(pars)} is not a set")
        self.lambda_helper = add_result_to_set
        self.lambda_pars = pars
        return self.visit(ctx.children[2])

    def visitExprFilter(self, ctx: LanguageParser.ExprFilterContext):
        pars = self.visit(ctx.children[4])
        if not isinstance(pars, frozenset):
            raise TypingError(f"{type(pars)} is not a set")
        self.lambda_helper = add_element_if_condition_true
        self.lambda_pars = pars
        return self.visit(ctx.children[2])

    """
        Set, get, add states. 'in'
    """

    def visitExprContains(self, ctx: LanguageParser.ExprContainsContext) -> bool:
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))

        if not isinstance(right, frozenset):
            raise TypingError(
                f"The second operand of `in` is {type(right)} rather than a set"
            )
        return left in right

    def visitExprSetStart(self, ctx: LanguageParser.ExprSetStartContext):
        graph = self.visit(ctx.expr(0))
        start_states = self.visit(ctx.expr(1))
        if not isinstance(start_states, frozenset):
            raise TypingError(f"Start states must be a set, not {type(start_states)}")
        if not isinstance(graph, EpsilonNFA):
            raise TypingError(f"set_start must operate on a graph, not {type(graph)}")
        new_graph = graph.copy()
        for start_state_to_remove in list(new_graph.start_states):
            new_graph.remove_start_state(start_state_to_remove)
        for start_state_to_add in start_states:
            new_graph.add_start_state(start_state_to_add)
        return new_graph

    def visitExprSetFinal(self, ctx: LanguageParser.ExprSetFinalContext):
        graph = self.visit(ctx.expr(0))
        final_states = self.visit(ctx.expr(1))
        if not isinstance(final_states, frozenset):
            raise TypingError(f"Final states must be a set, not {type(final_states)}")
        if not isinstance(graph, EpsilonNFA):
            raise TypingError(f"set_final must operate on a graph, not {type(graph)}")
        new_graph = graph.copy()
        for final_state_to_remove in list(new_graph.final_states):
            new_graph.remove_final_state(final_state_to_remove)
        for final_state_to_add in final_states:
            new_graph.add_final_state(final_state_to_add)
        return new_graph

    def visitExprAddStart(self, ctx: LanguageParser.ExprAddStartContext):
        graph = self.visit(ctx.expr(0))
        start_states = self.visit(ctx.expr(1))
        if not isinstance(start_states, frozenset):
            raise TypingError(f"Start states must be a set, not {type(start_states)}")
        if not isinstance(graph, EpsilonNFA):
            raise TypingError(f"add_start must operate on a graph, not {type(graph)}")
        new_graph = graph.copy()
        for start_state_to_add in start_states:
            new_graph.add_start_state(start_state_to_add)
        return new_graph

    def visitExprAddFinal(self, ctx: LanguageParser.ExprAddFinalContext):
        graph = self.visit(ctx.expr(0))
        final_states = self.visit(ctx.expr(1))
        if not isinstance(final_states, frozenset):
            raise TypingError(f"Final states must be a set, not {type(final_states)}")
        if not isinstance(graph, EpsilonNFA):
            raise TypingError(f"add_final must operate on a graph, not {type(graph)}")
        new_graph = graph.copy()
        for final_state_to_add in final_states:
            new_graph.add_final_state(final_state_to_add)
        return new_graph

    def visitExprGetStart(self, ctx: LanguageParser.ExprGetStartContext):
        nfa = self.visit(ctx.children[2])  # Original NFA
        if not isinstance(nfa, EpsilonNFA):
            raise TypingError(f"{type(nfa)} is not an NFA")
        return frozenset(state.value for state in nfa.start_states)

    def visitExprGetFinal(self, ctx: LanguageParser.ExprGetFinalContext):
        nfa = self.visit(ctx.children[2])  # Original NFA
        if not isinstance(nfa, EpsilonNFA):
            raise TypingError(f"{type(nfa)} is not an NFA")
        return frozenset(state.value for state in nfa.final_states)

    """
        Get nodes, edges, labels and Reachable
    """

    def visitExprGetNodes(self, ctx: LanguageParser.ExprGetEdgesContext):
        nfa = self.visit(ctx.children[2])
        if isinstance(nfa, EpsilonNFA):
            return frozenset(state.value for state in nfa.states)
        elif isinstance(nfa, WrapperRFA):
            return frozenset(self.build_rfa(nfa).get_states())
        else:
            raise TypingError(f"{type(nfa)} is not a supported automaton type")

    def visitExprGetEdges(self, ctx: LanguageParser.ExprGetEdgesContext):
        nfa = self.visit(ctx.children[2])
        if isinstance(nfa, EpsilonNFA):
            return frozenset(
                (from_state.value, label, to_state.value)
                for from_state, label, to_state in nfa
            )
        elif isinstance(nfa, WrapperRFA):
            return frozenset(self.build_rfa(nfa).get_edges())
        else:
            raise TypingError(f"{type(nfa)} is not a supported automaton type")

    def visitExprGetLabels(self, ctx: LanguageParser.ExprGetEdgesContext):
        nfa = self.visit(ctx.children[2])
        if isinstance(nfa, EpsilonNFA):
            return frozenset(label for _, label, _ in nfa)
        elif isinstance(nfa, WrapperRFA):
            return frozenset(label for _, label, _ in self.build_rfa(nfa).get_edges())
        else:
            raise TypingError(f"{type(nfa)} is not a supported automaton type")

    def visitExprGetReachable(self, ctx: LanguageParser.ExprGetReachableContext):
        graph = self.visit(ctx.expr())
        if not isinstance(graph, EpsilonNFA):
            raise TypingError(f"{type(graph)} is not a NFA")
        reachable_states = find_accessible_by_nfa(graph)
        return frozenset(reachable_states)

    """
        Operations with nfa ( &, |, ., *)
    """

    def visitExprUnion(self, ctx: LanguageParser.ExprUnionContext):
        fa1 = self.visit(ctx.expr(0))
        fa2 = self.visit(ctx.expr(1))
        if isinstance(fa1, EpsilonNFA) and isinstance(fa2, EpsilonNFA):
            return union(fa1, fa2)
        elif isinstance(fa1, WrapperRFA) and isinstance(fa2, WrapperRFA):
            return WrapperRFA(union(fa1.nfa, fa2.nfa))
        raise TypeError("Both operands must be of type EpsilonNFA or RSM")

    def visitExprConcat(self, ctx: LanguageParser.ExprConcatContext):
        fa1 = self.visit(ctx.expr(0))
        fa2 = self.visit(ctx.expr(1))
        if isinstance(fa1, EpsilonNFA) and isinstance(fa2, EpsilonNFA):
            return concat(fa1, fa2)
        elif isinstance(fa1, WrapperRFA) and isinstance(fa2, WrapperRFA):
            return WrapperRFA(concat(fa1.nfa, fa2.nfa))
        raise TypeError("Both operands must be of type EpsilonNFA or RSM")

    def visitExprStar(self, ctx: LanguageParser.ExprStarContext):
        fa = self.visit(ctx.expr())
        if isinstance(fa, EpsilonNFA):
            return apply_star(fa)
        elif isinstance(fa, WrapperRFA):
            return WrapperRFA(apply_star(fa.nfa))
        raise TypeError("The operand must be of type EpsilonNFA")

    def visitExprIntersect(self, ctx: LanguageParser.ExprIntersectContext):
        fa1 = self.visit(ctx.expr(0))
        fa2 = self.visit(ctx.expr(1))
        if isinstance(fa1, EpsilonNFA) and isinstance(fa2, EpsilonNFA):
            return intersect(fa1, fa2)
        elif isinstance(fa1, WrapperRFA) and isinstance(fa2, WrapperRFA):
            return WrapperRFA(intersect(fa1.nfa, fa2.nfa))
        raise TypeError("Both operands must be of type EpsilonNFA or RSM")

    """
        Index access
    """

    def visitExprIndex(self, ctx: LanguageParser.ExprIndexContext):
        ind = self.visit(ctx.children[3])
        edge = self.visit(ctx.children[0])
        if not isinstance(edge, Tuple):
            raise TypingError(f"Can't get index from {edge}.")
        return edge[ind]

    """
        Lift helper
    """

    def visitExprLift(self, ctx: LanguageParser.ExprLiftContext):
        val = self.visit(ctx.expr())
        if isinstance(val, str):
            fa = EpsilonNFA()
            fa.add_start_state(State(0))
            fa.add_final_state(State(1))
            fa.add_transition(State(0), Symbol(val), State(1))
            return fa
        elif isinstance(val, EpsilonNFA):
            return WrapperRFA(val)
        raise TypingError(f"{type(val).__name__} cannot be a symbol")
