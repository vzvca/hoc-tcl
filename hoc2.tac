# hoc stage 2 from "The Unix Programming Environment"
# (c) 2020 vzvca

%{
#!/usr/bin/tclsh

%}

%token NUMBER VAR NEWLINE
%right '='
%left  '+' '-'
%left '*' '/'
%left UNARYMINUS

%%

start: line NEWLINE start
 | line
 ;

line: expr    { puts " = $1" }
 | error      { puts " -- error" }
 |   # empty
 ;

expr: NUMBER { set _ $1 }
 | VAR              { set _ $::mem($1) }
 | VAR '=' expr     { set ::mem($1) $3 ; set _ $3 }
 | expr '+' expr    { set _ [expr {$1 + $3}] }
 | expr '-' expr    { set _ [expr {$1 - $3}] }
 | expr '*' expr    { set _ [expr {$1 * $3}] }
 | expr '/' expr    { set _ [expr {$1 / $3}] }
 | '(' expr ')'     { set _ $2 }
 | '-' expr %prec UNARYMINUS { set _ [expr -$2] }
 ;
 
%%

source hoc2.fcl.tcl
yyparse
