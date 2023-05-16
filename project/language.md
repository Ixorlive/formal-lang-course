# Описание языка
## Абстрактный синтаксис
```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool
  | Null 
  | Set of Set<val>
  | List if List<val>

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda =
    LambdaSimple of var * expr
    | LambdaMultiple of List<val> * expr
```
## Конкретный язык

```
prog: (stmt ';')* EOF;

stmt:  bind | print;

bind: var '=' expr;
print: 'print' '(' expr ')';

int: [0-9]+;
char: [a-zA-Z];
string: '"' .*? '"';
bool: 'true' | 'false';
set: '{' '}' | '{' set_elem (',' set_elem)*  '}';
set_elem: int | int '..' int;
list: '[' ']' | '[' val (',' val)* ']';

val := string
     | int
     | bool
     | 'null'
     | set
     | list;

var: char (char | [0-9] | '_')*;

expr := var
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
      | 'load' '(' string ')'
      | '!' expr
      | expr '&' expr   // intersect
      | expr '.' expr   // concat
      | expr '|' expr   // union
      | expr '*'        // star
      | expr 'in' expr  // contains     
      | var '[' int ']' // index of list

lambda := pattern '=>' expr | '(' lambda ')';
pattern: var | '(' pattern (',' pattern)* ')';
```

## Примеры

Загрузить граф:
```
g = load("path/to/graph.txt");
print(get_vertices(g));
```
Установить стартовые вершины
```
start(g, {1,2,3});
```
Добавить стартовые вершины
``` 
add_start(g, {7,8});
```
Получить стартовые вершины
``` 
print(get_start(g));
```
Фильтрация вершин 
```
filtered = filter((v) => v > 5, get_vertices(g));
print(filtered);
```
Применение функции ко всем вершинам
```
mapped = map((v) => v * 2, get_vertices(g));
print(mapped);
```
Пересечение
```
g1 = load("path/to/graph1.txt");
g2 = load("path/to/graph2.txt");
intersected = g1 & g2;
print(get_edges(intersected));
```
Объединение двух графиков
```
g1 = load("path/to/graph1.txt");
g2 = load("path/to/graph2.txt");
concatenated = g1 . g2;
print(get_edges(concatenated));
```
Замыкания к графику
```
g = load("path/to/graph.txt");
starred = g *;
print(get_edges(starred));
```
Пример из условия задачи (не уверен, что правильно понял пример)
```
g' = load("wine");
g = start(final(g', get_vertices(g')), {0,1,...,100});
l1 = "l1" | "l2";
q1 = ("type" | l1)*;
q2 = "sub_class_of" . l1;
res1 = g & q1;
res2 = g & q2;
print(res1);
s = get_start(g);
vertices1 = filter((v) => v in s, map((edge) => edge[0][0], get_edges(res1)));
vertices2 = filter((v) => v in s, map((edge) => edge[0][0], get_edges(res2)));
vertices = vertices1 & vertices2;
print(vertices);
```
