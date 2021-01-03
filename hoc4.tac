# hoc stage 4 from "The Unix Programming Environment"
# (c) 2020 vzvca

%{
#!/usr/bin/tclsh

array set ::mem {
    PI  3.14159265358979323846
    E   2.7182818284590452354
    LN2 0.693147180559945309417
    DEG 57.29577951308232087680
    PHI 1.611803398874989484820
}
%}

%token NUMBER VAR BLTIN NEWLINE
%right '='
%left  '+' '-'
%left  '*' '/'
%left UNARYMINUS
%right '^'
%%

start: line NEWLINE start
 | line
 ;

line: expr    { puts " = $1" }
 | asgn
 | error      { puts " -- error" }
 |   # empty
 ;

asgn: VAR '=' expr     { set ::mem($1) $3 ; set _ $3 }
 ;

expr: NUMBER { code push $1 }
 | VAR {
       set failed [catch { set _ $::mem($1) }]
       if { $failed } {
       	  puts "undefined variable $1"
       }
 }
 | asgn
 | BLTIN '(' expr ')' { code push ::tcl::mathfunc::$1 push $3 invokeStk 2 }
 | expr '+' expr    { code add }
 | expr '-' expr    { code sub }
 | expr '*' expr    { code mul }
 | expr '/' expr    { code div }
 | expr '^' expr    { code expon }
 | '(' expr ')'     { set _ $2 }
 | '-' expr %prec UNARYMINUS { set _ [expr -$2] }
 ;
 
%%

source hoc4.fcl.tcl
yyparse
