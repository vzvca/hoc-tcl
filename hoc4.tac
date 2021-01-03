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

set ::todo {}

proc code { args } {
     lappend ::todo {*}$args ";"
}	     

proc asm {} {
     set res [::tcl::unsupported::assemble [join $::todo]]
     set ::todo {}
     return $res
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

line: expr    { puts " = [asm]" }
 | asgn       { asm }
 | error      { puts " -- error" }
 |   # empty
 ;

asgn: VAR '=' expr     { code push $1 ; code push ::mem ; code reverse 3 ; code storeArrayStk }
 ;

expr: NUMBER { code push $1 }
 | VAR { code push ::mem ; code push $1 ; code loadArrayStk }
 | asgn
 | BLTIN '(' expr ')' { code push ::tcl::mathfunc::$1 ; code reverse 2 ; code invokeStk 2 }
 | expr '+' expr    { code add }
 | expr '-' expr    { code sub }
 | expr '*' expr    { code mult }
 | expr '/' expr    { code div }
 | expr '^' expr    { code expon }
 | '(' expr ')'     
 | '-' expr %prec UNARYMINUS { code uminus }
 ;
 
%%

source hoc4.fcl.tcl
yyparse
