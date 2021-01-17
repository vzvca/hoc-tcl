# hoc stage 7 from "The Unix Programming Environment"
# (c) 2020 vzvca

%{
#!/usr/bin/tclsh

set ::PI  3.14159265358979323846
set ::E   2.7182818284590452354
set ::LN2 0.693147180559945309417
set ::DEG 57.29577951308232087680
set ::PHI 1.611803398874989484820
set ::EPS 1e-6

set ::debug 0
set ::todo {}

proc code { args } {
     if { $::debug } { puts $args }
     lappend ::todo {*}$args ";"
}	     

proc getcode {} {
    set code [join $::todo]
    set ::todo {}
    return $code
}

proc asm {} {
    return [::tcl::unsupported::assemble [getcode]]
}

proc opassign { op var } {
    if { [islocal $var] } {
	code load $var
	code reverse 2 ; code $op
	code store $var
    } else {
	code push ::$var ; code loadStk
	code reverse 2 ; code $op
	code push ::$var ; code reverse 2 ; code storeStk
    }
}

proc epstst { op } {
     code sub ; code push ::tcl::mathfunc::abs ; code reverse 2 ; code invokeStk 2
     code push ::EPS ; code loadStk
     code $op
}

# -- nested control structure support
set ::nblk   0
set ::nested {}
proc startblk { what } {
     set blk [incr ::nblk]
     lappend ::nested [list "type" $what "idx" $blk]
     return $blk
}
proc endblk {} {
     set ::nested [lrange $::nested 0 end-1]
}
proc curblk {} {
     return [lindex $::nested end]
}
proc curblki {} {
     return [dict get [curblk] "idx"]
}
proc indefn {} {
     set fblk ""
     foreach blk $::nested {
     	 set what [dict get $blk "type"]
	 if { $what eq "func" } { set fblk $what }
     }
     expr {$fblk eq "func"}
}
proc check_func { token } {
     if { ![indefn] } {
     	error "$token outside function definition"
     }
}
proc check_loop { token } {
    set fblk ""
    foreach blk $::nested {
	set what [dict get $blk "type"]
	if { $what eq "func" } { set fblk "" ; continue }
	if { ($what eq "while") || ($what eq "do") } { set fblk "loop" }
    }
    if { $fblk ne "loop" } {
	error "$token invoked outside of a loop"
    }
}
proc check { what token } {
    set blk [lindex $::nested end]
    if { $what ne [dict get $blk what] } {
       error "$token expected at $what level only"
    }
}
proc curdefnblki {} {
     foreach blk $::nested {
         set what [dict get $blk "type"]
	 set blki [dict get $blk "idx"]
	 if { $what eq "func" } { set res $blki }
     }
     return $res
}
proc curloopblki {} {
    foreach blk $::nested {
         set what [dict get $blk "type"]
	 set blki [dict get $blk "idx"]
	if { ($what eq "while") || ($what eq "do") } { set res $blki }
    }
    return $res
}
proc islocal { var } {
}
%}

%token NUMBER READ IDENT BLTIN PROCNAME VARNAME NEWLINE DO WHILE IF ELSE FUNC RETURN ARG LBRACKET RBRACKET STRING INCR DECR BREAK CONTINUE
%right '=' ADDASSIGN SUBASSIGN MULASSIGN DIVASSIGN LSRASSIGN LSLASSIGN MODASSIGN
%left OR
%left AND
%left GT GE LT LE EQ EPSEQ NE EPSNE
%left  '+' '-'
%left  '*' '/' '%' LSL LSR
%left UNARYMINUS NOT
%right '^'
%%
start: list ;

list:  # empty
 | list NEWLINE
 | list defn  { }
 | list stmt  { asm }
 | list expr  { puts " = [asm]" }
 | list error { puts " -- error" }
 ;
 
asgn:
   IDENT '=' expr  { if {[islocal $1]} { code store $1 } else { code push ::$1 ; code reverse 2 ; code storeStk } }
 | IDENT ADDASSIGN expr { opassign add $1 } 
 | IDENT SUBASSIGN expr { opassign sub $1 } 
 | IDENT MULASSIGN expr { opassign mult $1 } 
 | IDENT DIVASSIGN expr { opassign div $1 } 
 | IDENT MODASSIGN expr { opassign mod $1 } 
 | IDENT LSLASSIGN expr { opassign lshift $1 } 
 | IDENT LSRASSIGN expr { opassign rshift $1 } 
 ;

defn:
   func PROCNAME '(' arglist ')' stmt {
       code label be_[curblki]
       set blk [curblk]
       proc $2 [dict get $blk args] [list ::tcl::unsupported::assemble [getcode]]
       endblk
   }
 ;

func: FUNC { startblk func }
 ; 

identlist: { set _ {} }
 | IDENT { set _ $1 }
 | identlist ',' IDENT { set _ $1 ; lappend _ $3 }
 ;

arglist: identlist { set blk [curblk] ; dict set blk args $1 ; lset ::nested end end $blk }
 ;

stmt: expr { code pop }
 | RETURN { check_func return ; code push 0 ; code jump be_[curdefnblki]  }
 | RETURN expr { check_func return ; code jump be_[curdefnblki] }
 | while cond stmt { code jump bs_[curblki] ; code label bf_[curblki] ; code label be_[curblki] ; endblk  }
 | do stmt while cond { code jumpTrue bs_[curblki] ; code label bf_[curblki] ; code label be_[curblki] ; endblk }
 | if cond stmt else stmt { code label be_[curblki] ; endblk }
 | if cond stmt { code label bf_[curblki] ; endblk }
 | BREAK { check_loop break ; code jump be_[curloopblki] }
 | CONTINUE { check_loop continue ; code jump bs_[curloopblki] }
 | LBRACKET stmtlist RBRACKET {}
 | VAR identlist { check var func ; set blk [curblk] ; dict lappend blk locals {*}$2 ; lreplace ::nested end $blk }
 ;

if: IF { startblk if }
 ;

else: ELSE { code jump be_[curblki] ; code label bf_[curblki] }
 ;

do: DO { startblk do ; code label bs_[curblki] }
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

procname: PROCNAME { code push $1 }
 ;

bltin: BLTIN { code push ::tcl::mathfunc::$1 }
 ;

and: AND { startblk and ; code dup ; code push 0 ; code eq ; code jumpTrue be_[curblki] }
 ;

or: OR { startblk and ; code dup ; code push 0 ; code ne ; code jumpTrue be_[curblki] }
 ;

ternaryTrue: '?' { startblk ? ; code jumpFalse bf_[curblki] }
 ;

ternaryFalse: ':' { code jump be_[curblki] ; code label bf_[curblki] }
 ;

expr:
   NUMBER { code push $1 }
 | STRING { code push $1 }
 | procname '(' arglist ')' { code invokeStk [incr 3] }
 | INCR IDENT {
      if {[islocal $2]} {
         code incrImm $2 1
      } else {
         push ::$2 ; code incrStkImm 1
      }
 }
 | DECR IDENT { if {[islocal $2]} { code incrImm $2 -1 } else { push ::$2 ; code incrStkImm -1 } }
 | VARNAME INCR {
      if {[islocal $1]} {
          code load $1 ; code incrImm $1 1 ; code pop
      } else {
         code push ::$1 ; code loadStk 
	 code push ::$1 ; code incrStkImm 1 ; code pop
      }
 }
 | VARNAME DECR {
      if {[islocal $1]} {
          code load $1 ; code incrImm $1 -1 ; code pop
      } else {
         code push ::$1 ; code loadStk 
	 code push ::$1 ; code incrStkImm -1 ; code pop
      }
 }
 | asgn
 | IDENT { is {[islocal $2]} { code load $2 } else { code push ::$2 ; code loadStk }
 | ARG { code load $1 }
 | READ '(' IDENT ')'   { doread $1 }
 | bltin '(' ')' { code invokeStk 1 }
 | bltin '(' expr ')' { code invokeStk 2 }
 | bltin '(' expr ',' expr ')' { code invokeStk 3 }
 | expr '+' expr      { code add }
 | expr '-' expr      { code sub }
 | expr '*' expr      { code mult }
 | expr '/' expr      { code div }
 | expr '^' expr      { code expon }
 | expr '%' expr      { code mod }
 | expr LSL expr      { code lshift }
 | expr LSR expr      { code rshift }
 | expr ternaryTrue expr ternaryFalse expr { code label be_[curblki] ; endblk }
 | '(' expr ')'     
 | '-' expr %prec UNARYMINUS { code uminus }
 | expr GT expr       { code gt }
 | expr GE expr       { code ge }
 | expr LT expr       { code lt }
 | expr LE expr       { code le }
 | expr EQ expr       { code eq }
 | expr NE expr       { code neq }
 | expr EPSEQ expr    { epstst le }
 | expr EPSNE expr    { epstst gt }
 | expr and expr      { code land ; code label be_[curblki] ; endblk }
 | expr or expr       { code lor  ; code label be_[curblki] ; endblk }
 | NOT expr           { code not }
 ;
 
%%

source hoc7.fcl.tcl

set debug 0
proc main {} {
    set files [list]
    foreach arg $::argv {
       if { $arg eq "-d" } {
	   incr ::debug
       } else {
	   lappend files $arg
       }
    }

    foreach fname $files {
	if { $fname ne "-" } {
	    set fin [open $fname "r"]
	    fconfigure $fin -buffering line
	    yyrestart $fin
	    yyparse
	    close $fin
	} else {
	    yyrestart stdin
	    set files {}
	    break
	}
    }

    if { [llength $files] == 0 } {
	while 1 {
	    set failed [catch { yyparse } msg]
	    if { $failed } { puts $msg }
	}
    }
}

main
