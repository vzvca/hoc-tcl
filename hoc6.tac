# hoc stage 6 from "The Unix Programming Environment"
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
     puts $args
     lappend ::todo {*}$args ";"
}	     

proc asm {} {
     set res [::tcl::unsupported::assemble [join $::todo]]
     set ::todo {}
     return $res
}

# -- nested control structure support
set ::nblk   0
set ::nested {}
proc startblk { what } {
     set blk [incr ::nblk]
     lappend ::nested [list $what $blk]
     return $blk
}
proc endblk {} {
     set ::nested [lrange $::nested 0 end-1]
}
proc curblk {} {
     return [lindex $::nested end]
}
proc curblki {} {
     return [lindex [curblk] end]
}
proc indefn { func_or_proc } {
     set fblk ""
     foreach blk $::nested {
     	 set what [lindex $blk 0]
	 if { $what eq "proc" || $what eq "func" } { set fblk $what }
     }
     expr {$fblk eq $func_or_proc}
}
proc check_return { what } {
     if { ![indefn $what] } {
     	error "return outside procedure / function definition"
     }
}
proc curdefnblki {} {
     foreach blk $::nested {
         lassign $blk what blki
	 if { $what eq "proc" || $what eq "func" } { set res $blki }
     }
     return $res
}
%}

%token NUMBER PRINT READ VAR BLTIN NEWLINE WHILE IF ELSE PROC FUNC RETURN ARG PROCNAME LBRACKET RBRACKET
%right '='
%left OR
%left AND
%left GT GE LT LE EQ NE
%left  '+' '-'
%left  '*' '/'
%left UNARYMINUS NOT
%right '^'
%%
start: list ;

list:  # empty
 | list NEWLINE
 | list defn  { }
 | list asgn  { asm }
 | list stmt  { asm }
 | list expr  { puts " = [asm]" }
 | list error        { puts " -- error" }
 ;
 
asgn:
   VAR '=' expr  { code push $1 ; code push ::mem ; code reverse 3 ; code storeArrayStk }
 ;

defn:
   func VAR '(' ')' stmt {
       code label be_[curblki]
       proc $2 args [subst -novariables {lassign $args 1 2 3 4 5 6 7 8 9 ; ::tcl::unsupported::assemble {[join $::todo]}}]
       set ::todo {}
       endblk
   }
 | proc VAR '(' ')' stmt {
       code label be_[curblki]
       proc $2 args [subst -novariables {lassign $args 1 2 3 4 5 6 7 8 9 ; ::tcl::unsupported::assemble {[join $::todo]}}]
       set ::todo {}
       endblk
   }
 ;

func: FUNC { startblk func } ;
proc: PROC { startblk proc } ;

stmt: expr { code pop }
 | RETURN { check_return proc ; code jump be_[curdefnblki]  }
 | RETURN expr { check_return func ; code jump be_[curdefnblki] }
 | PRINT expr { code push puts ; code reverse 2 ; code invokeStk 2 ; code pop}
 | while cond stmt { code jump bs_[curblki] ; code label bf_[curblki] ; endblk  }
 | if cond stmt else stmt { code label be_[curblki] ; endblk }
 | if cond stmt { code label bf_[curblki] ; endblk }
 | LBRACKET stmtlist RBRACKET {}
 ;

if: IF { startblk if }
 ;

else: ELSE { code jump be_[curblki] ; code label bf_[curblki] }
 ;

while: WHILE { startblk while ; code label bs_[curblki] }
 ;

cond: '(' expr ')' { code jumpFalse bf_[curblki] ; code label bt_[curblki] }
 ;

stmtlist: # nothing
 | stmtlist NEWLINE
 | stmtlist stmt
 ;

arglist: { set _ 0 }
 | expr          { set _ 1 }
 | arglist ',' expr { set _ $1 ; incr _ }
 ;

procname: PROCNAME { code push $1 } ;

expr:
   NUMBER { code push $1 }
 | procname '(' arglist ')' { code invokeStk [incr 3] }
 | VAR { code push ::mem ; code push $1 ; code loadArrayStk }
 | ARG { code load $1 }
 | asgn
 | READ '(' VAR ')'   { error NYI }
 | BLTIN '(' expr ')' { code push ::tcl::mathfunc::$1 ; code reverse 2 ; code invokeStk 2 }
 | expr '+' expr      { code add }
 | expr '-' expr      { code sub }
 | expr '*' expr      { code mult }
 | expr '/' expr      { code div }
 | expr '^' expr      { code expon }
 | '(' expr ')'     
 | '-' expr %prec UNARYMINUS { code uminus }
 | expr GT expr       { code gt }
 | expr GE expr       { code ge }
 | expr LT expr       { code lt }
 | expr LE expr       { code le }
 | expr EQ expr       { code eq }
 | expr NE expr       { code neq }
 | expr AND expr      { code land }
 | expr OR expr       { code lor }
 | NOT expr           { code not }
 ;
 
%%

source hoc6.fcl.tcl
yyparse
