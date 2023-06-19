from typing import TextIO
import io

from antlr4 import InputStream, CommonTokenStream

from project.antlr.LanguageLexer import LanguageLexer
from project.antlr.LanguageParser import LanguageParser
from project.executor_visitor import ExecutorVisitor, TypingError
from project.error_checker_visitor import ErrorCheckerVisitor


def execute_program(
    program_context: LanguageParser.ProgramContext, output_stream: TextIO
):
    error_checker = ErrorCheckerVisitor()
    error_checker.visit(program_context)
    if error_checker.has_error:
        print("Execution stopped due to errors.", file=output_stream)
        return

    program_executor = ExecutorVisitor(output_stream)
    try:
        program_executor.visit(program_context)
    except TypingError as typing_error:
        print(typing_error, file=output_stream)
        print("Execution stopped due to previous error.", file=output_stream)
        return


def generate_parse_tree(input_stream: InputStream, suppress_errors=False):
    lexer = LanguageLexer(input_stream)
    if suppress_errors:
        lexer.removeErrorListeners()
    token_stream = CommonTokenStream(lexer)
    parser = LanguageParser(token_stream)
    if suppress_errors:
        parser.removeErrorListeners()
    return parser.program()


def execute_from_stream(input_stream: InputStream, output_stream: TextIO):
    parse_tree = generate_parse_tree(input_stream)
    execute_program(parse_tree, output_stream)


def execute_from_string(input_str: str, output_stream: TextIO):
    execute_from_stream(InputStream(input_str), output_stream)


def execute_string_and_return_result(input_str: str) -> str:
    with io.StringIO() as output_stream:
        execute_from_string(input_str, output_stream)
        return output_stream.getvalue()
