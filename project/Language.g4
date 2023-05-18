grammar Language;

program: (stmt ';')* EOF;

stmt:  bind | print;

bind: var '=' expr;
print: 'print' '(' expr ')';

literal: INT | STRING | BOOL | set | list;

set: '{' '}' | '{' set_elem (',' set_elem)*  '}';
set_elem: literal | INT '..' INT;

list: '[' ']' | '[' literal (',' literal)* ']';

val: literal | 'null';

VAR_NAME: [a-zA-Z_][a-zA-Z_0-9]*;
var: VAR_NAME;

expr: var
      | val
      | '(' expr ')'
      | 'start' '(' expr ',' expr ')'
      | 'final' '(' expr ',' expr ')'
      | 'add_start' '(' expr ',' expr ')'
      | 'add_final' '(' expr ',' expr ')'
      | 'get_start' '(' expr ')'
      | 'get_final' '(' expr ')'
      | 'get_reachable' '(' expr ')'
      | 'get_vertices' '(' expr ')'
      | 'get_edges' '(' expr ')'
      | 'get_labels' '(' expr ')'
      | 'map' '(' lambda ',' expr ')'
      | 'filter' '(' lambda ',' expr ')'
      | 'load' '(' STRING ')'
      | '!' expr
      | expr '&' expr   // intersect
      | expr '.' expr   // concat
      | expr '|' expr   // union
      | expr '*'        // star
      | expr 'in' expr  // contains
      | expr '[' INT ']'; // index of list


lambda:
    pattern '=>' expr
    | '(' lambda ')';
pattern:
    var
    | '(' pattern (',' pattern)* ')';

BLOCK_COMMENT: '/*' (BLOCK_COMMENT|.)*? '*/' -> skip;
COMMENT: '//' .*? ('\n'|EOF) -> skip;
WS: [ \r\n\t]+ -> skip;
INT: [0-9]+;
CHAR: [a-zA-Z];
STRING: '"' ~["]* '"';
BOOL: 'true' | 'false';
