grammar Language;

program: (stmt ';')* EOF;

stmt:  bind | print;

bind: var '=' expr;
print: 'print' '(' expr ')';

lambda:
    pattern '=>' expr                   # lambdaExpr
    | '(' lambda ')'                    # lambdaParens;
pattern:
    var                                 # patternVar
    | '(' pattern (',' pattern)* ')'    # patternTuple;

literalInt: INT;
literalString: STRING;
literalRec: 'rec' '(' var ')';
literal: literalInt | literalString | literalRec | set;

set: '{' '}' | '{' set_elem (',' set_elem)*  '}';
set_elem:
    literal                             # setElemLit
    | literalInt '..' literalInt        # setElemRange;

val: literal | 'null';
var: VAR_NAME;

expr: var                                   # exprVar
      | val                                 # exprVal
      | '(' expr ')'                        # exprExpr
      | 'set_start' '(' expr ',' expr ')'   # exprSetStart
      | 'set_final' '(' expr ',' expr ')'   # exprSetFinal
      | 'add_start' '(' expr ',' expr ')'   # exprAddStart
      | 'add_final' '(' expr ',' expr ')'   # exprAddFinal
      | 'get_start' '(' expr ')'            # exprGetStart
      | 'get_final' '(' expr ')'            # exprGetFinal
      | 'get_reachable' '(' expr ')'        # exprGetReachable
      | 'get_nodes' '(' expr ')'            # exprGetNodes
      | 'get_edges' '(' expr ')'            # exprGetEdges
      | 'get_labels' '(' expr ')'           # exprGetLabels
      | 'map' '(' lambda ',' expr ')'       # exprMap
      | 'filter' '(' lambda ',' expr ')'    # exprFilter
      | 'load' '(' literalString ')'               # exprLoad
      | '!' expr                            # exprNot
      | expr '&' expr                       # exprIntersect
      | expr '.' expr                       # exprConcat
      | expr '|' expr                       # exprUnion
      | expr '*'                            # exprStar
      | expr 'in' expr                      # exprContains
      | expr '[' literalInt ']'             # exprIndex
      | expr '{' expr (',' expr)* '}'       # exprSet
      | 'lift' '(' expr ')'                 # exprLift;


VAR_NAME: [a-zA-Z_][a-zA-Z_0-9]*;
BLOCK_COMMENT: '/*' (BLOCK_COMMENT|.)*? '*/' -> skip;
COMMENT: '//' .*? ('\n'|EOF) -> skip;
WS: [ \r\n\t]+ -> skip;
INT: [0-9]+;
CHAR: [a-zA-Z];
STRING: '"' ~["]* '"';
