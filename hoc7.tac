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
     if { $::debug == 1 } { puts $args }
     lappend ::todo {*}$args ";"
}
# build the list of global variables used in a function.
# returns empty list if not called from a function.
proc globals {} {
    if { ![indefn] } { return {} }
    puts "globals on [curblk]"
    set lst [dict get [curblk] "args"]
    lappend lst {*}[dict get [curblk] "locals"]
    set res {}
    foreach var [dict get [curblk] "idents"] {
	if { [lsearch $lst $var] == -1 } {
	    lappend res $var
	}
    }
    return $res
}
proc getcode {} {
    set code ""
    # add prolog to perform upvar for global variables
    foreach var [globals] {
	append code "push #0 ; push $var ; upvar $var ; pop ; "
    }
    append code [join $::todo]
    if { $::debug == 2 } { puts $code }
    set ::todo {}
    return $code
}
proc asm {} {
    return [::tcl::unsupported::assemble [getcode]]
}

proc opassign { op var } {
    if { [indefn] } {
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
    set blki [incr ::nblk]
    if { $what ne "func" } {
	set blk [dict create "type" $what "idx" $blki]
    } else {
	set blk [dict create "type" $what "idx" $blki "args" {} "locals" {} "idents" {}]
    }
    lappend ::nested $blk
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
proc curdefnblk {} {
    set fblk [dict create "type" "none"]
    foreach blk $::nested {
	set what [dict get $blk "type"]
	if { $what eq "func" } { set fblk $blk }
    }
    return $fblk
}
proc indefn {} {
    set fblk [curdefnblk]
    set what [dict get $fblk "type"]
    expr {$what eq "func"}
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
    if { [indefn] } {
	set lst [dict get [curblk] "args"]
	if { [lsearch $lst $var] != -1 } { return 1 }
	set lst [dict get [curblk] "locals"]
	if { [lsearch $lst $var] != -1 } { return 1 }	
    } 
    return 0
}
proc blkindex { idx } {
    set cnt 0
    foreach blk $::nested {
	if { [dict get $blk "idx"] == $idx } { return $cnt }
	incr cnt
    }
    return -1
}
proc addvar { var } {
    if { ![indefn] } return
    set blk [curdefnblk]
    set lst [dict get $blk "args"]
    if { [lsearch $lst $var] != -1 } return
    set lst [dict get $blk "locals"]
    if { [lsearch $lst $var] != -1 } return
    set lst [dict get $blk "idents"]
    if { [lsearch $lst $var] != -1 } return
    dict lappend blk "idents" $var
    lset ::nested [blkindex [curdefnblki]] $blk
}
%}

%token NUMBER READ IDENT BLTIN PROCNAME VARNAME NEWLINE DO WHILE IF ELSE FUNC RETURN LBRACKET RBRACKET STRING INCR DECR BREAK CONTINUE LOCAL
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

ident: IDENT { addvar $1 }
 ;

varname: VARNAME { addvar $1 }
 ;

asgn:
   ident '=' expr  { if {[indefn]} { code store $1 } else { code push ::$1 ; code reverse 2 ; code storeStk } }
 | ident ADDASSIGN expr { opassign add $1 } 
 | ident SUBASSIGN expr { opassign sub $1 } 
 | ident MULASSIGN expr { opassign mult $1 } 
 | ident DIVASSIGN expr { opassign div $1 } 
 | ident MODASSIGN expr { opassign mod $1 } 
 | ident LSLASSIGN expr { opassign lshift $1 } 
 | ident LSRASSIGN expr { opassign rshift $1 } 
 ;

defn:
   func PROCNAME '(' argdeflist ')' stmt {
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

argdeflist: identlist { set blk [curblk] ; dict set blk "args" $1 ; lset ::nested end $blk }
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
 | LOCAL identlist { check var func ; set blk [curblk] ; dict lappend blk "locals" {*}$2 ; lset ::nested end $blk }
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
 | INCR ident {
      if {[indefn]} {
         code incrImm $2 1
      } else {
         code push ::$2 ; code incrStkImm 1
      }
 }
 | DECR ident { 
      if {[indefn]} {
         code incrImm $2 -1
      } else {
         code push ::$2 ; code incrStkImm -1
      }
 }
 | varname INCR {
      if {[indefn]} {
          code load $1 ; code incrImm $1 1 ; code pop
      } else {
         code push ::$1 ; code loadStk 
	 code push ::$1 ; code incrStkImm 1 ; code pop
      }
 }
 | varname DECR {
      if {[indefn]} {
          code load $1 ; code incrImm $1 -1 ; code pop
      } else {
         code push ::$1 ; code loadStk 
	 code push ::$1 ; code incrStkImm -1 ; code pop
      }
 }
 | asgn
 | ident { if {[indefn]} { code load $1 } else { code push ::$1 ; code loadStk } }
 | READ '(' ident ')'   { code push "gets" ; code push "stdin" ; code push $3 ; code invokeStk 3 }
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
