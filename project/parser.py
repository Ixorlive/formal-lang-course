from typing import Union

from antlr4 import FileStream, InputStream, CommonTokenStream
from antlr4.error.Errors import ParseCancellationException

from project.antlr.LanguageLexer import LanguageLexer
from project.antlr.LanguageParser import LanguageParser
from project.antlr.LanguageVisitor import LanguageVisitor


def parse_file(file_path):
    input_stream = FileStream(file_path)
    return parse_input_stream(input_stream)


def parse_string(input_string):
    input_stream = InputStream(input_string)
    return parse_input_stream(input_stream)


def parse_console():
    input_string = input("Enter text to parse: ")
    return parse_string(input_string)


def parse_input_stream(input_stream):
    lexer = LanguageLexer(input_stream)
    lexer.removeErrorListeners()
    token_stream = CommonTokenStream(lexer)
    parser = LanguageParser(token_stream)
    return parser


def check_correction_file(file_path):
    input_stream = FileStream(file_path)
    return check_correction(input_stream)


def check_correction_string(input_string):
    input_stream = InputStream(input_string)
    return check_correction(input_stream)


def check_correction_console():
    input_string = input("Enter text to parse: ")
    return check_correction_string(input_string)


def check_correction(input_stream) -> bool:
    parser = parse_input_stream(input_stream)
    parser.removeErrorListeners()
    _ = parser.program()
    return not parser.getNumberOfSyntaxErrors()


class DotGeneratingVisitor(LanguageVisitor):
    def __init__(self):
        self.graph = []
        self.node_counter = 0
        self.node_ids = {}

    def generic_visit(self, node_name, ctx):
        node_id = self.node_counter
        self.node_ids[ctx] = node_id
        self.node_counter += 1

        label = f"{node_name}: {ctx.getText()}" if ctx.children is None else node_name
        self.graph.append(f'{node_id} [label="{label}"]')

        if not isinstance(ctx.parentCtx, type(None)):
            parent_id = self.node_ids.get(ctx.parentCtx, None)
            if parent_id is not None:
                self.graph.append(f"{parent_id} -> {node_id}")

        return self.visitChildren(ctx)

    def visitProgram(self, ctx: LanguageParser.ProgramContext):
        return self.generic_visit("program", ctx)

    def visitBind(self, ctx: LanguageParser.BindContext):
        return self.generic_visit("=", ctx)

    def visitStmt(self, ctx: LanguageParser.StmtContext):
        return self.generic_visit("Stmt", ctx)

    def visitPrint(self, ctx: LanguageParser.PrintContext):
        return self.generic_visit("print", ctx)

    def visitLiteral(self, ctx: LanguageParser.LiteralContext):
        return self.generic_visit("Literal: " + ctx.getText().replace('"', "'"), ctx)

    def visitSet(self, ctx: LanguageParser.SetContext):
        return self.generic_visit("Set " + ctx.getText(), ctx)

    def visitSet_elem(self, ctx: LanguageParser.Set_elemContext):
        return self.generic_visit(ctx.getText(), ctx)

    def visitList(self, ctx: LanguageParser.ListContext):
        return self.generic_visit("List " + ctx.getText(), ctx)

    def visitVal(self, ctx: LanguageParser.ValContext):
        return self.generic_visit("Val " + ctx.getText().replace('"', "'"), ctx)

    def visitVar(self, ctx: LanguageParser.VarContext):
        return self.generic_visit("Var: " + ctx.getText().replace('"', "'"), ctx)

    def visitExpr(self, ctx: LanguageParser.ExprContext):
        return self.generic_visit("Expr: " + ctx.getText().replace('"', "'"), ctx)

    def visitLambda(self, ctx: LanguageParser.LambdaContext):
        return self.generic_visit("Lambda", ctx)

    def visitPattern(self, ctx: LanguageParser.PatternContext):
        return self.generic_visit("lambda_pattern", ctx)

    def get_dot_graph(self):
        return "digraph {\n" + "\n".join(self.graph) + "\n}"


def generate_dot_text(input_stream: Union[str, InputStream], from_file: bool = False):
    if isinstance(input_stream, str):
        if from_file:
            input_stream = FileStream(input_stream)
        else:
            input_stream = InputStream(input_stream)
    if not check_correction(input_stream):
        raise ParseCancellationException("Syntax error")
    input_stream.seek(0)
    parse_tree = parse_input_stream(input_stream).program()
    visitor = DotGeneratingVisitor()
    visitor.visit(parse_tree)
    return visitor.get_dot_graph()


def generate_dot(
    input_stream: Union[str, InputStream],
    from_file: bool = False,
    output: str = "output.dot",
):
    with open(output, "w") as file:
        file.write(generate_dot_text(input_stream, from_file))
