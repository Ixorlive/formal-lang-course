from project.antlr.LanguageVisitor import LanguageVisitor


class ErrorCheckerVisitor(LanguageVisitor):
    def __init__(self):
        self.has_error = False

    def visitErrorNode(self, node):
        self.has_error = True
