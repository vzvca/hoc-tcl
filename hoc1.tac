# hoc stage 1 from "The Unix Programming Environment"
# (c) 2020 vzvca

%{
#!/usr/bin/tclsh

%}

%token NUMBER NEWLINE

%%

start: line NEWLINE start
 | line
 ;

line: expr    { puts " = $1" }
 | error      { puts " -- error" }
 |   # empty
 ;

expr: NUMBER { set _ $1 }
 | expr '+' expr    { set _ [expr {$1 + $3}] }
 | expr '-' expr    { set _ [expr {$1 - $3}] }
 | expr '*' expr    { set _ [expr {$1 * $3}] }
 | expr '/' expr    { set _ [expr {$1 / $3}] }
 | '(' expr ')'     { set _ $2 }
 ;
 
%%

source hoc1.fcl.tcl
yyparse
