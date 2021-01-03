# hoc-tcl
Port of hoc from "The Unix Programming Environment" book to TCL using taccle/fickle yacc/lex TCL clones.

Chapter 8 of the book by Brian W. Kernihgan & Rob Pike is devoted to program development. Along the chapter, the reader learns how to use yacc, lex and make, starting form a basic 4 functions interactive calculator and ending with a small but quite capable programming language including control flow and functions. This language is called hoc. 

There are 6 stages in hoc development with increasing complexity and functionality. Starting at stage 4 a bytecode engine is added, in this project I used the TCL builtin bytecode engine which is available at the script level using `::tcl::unsupported::assemble` since Tcl 8.6.3.

## Stage 1

This 1st increment is derived both from taccle example `interactive_calculator.tac` and hoc stage 1.

To build hoc1 use :
````
$ make hoc1
tclsh ./fickle/fickle.tcl -o hoc1.fcl.tcl hoc1.fcl
tclsh ./taccle/taccle.tcl -d -v -w -o hoc1.tac.tcl hoc1.tac
Shift/Reduce error in state 15 between rule 9 and token "+", resolved as shift.
Shift/Reduce error in state 15 between rule 9 and token "-", resolved as shift.
Shift/Reduce error in state 15 between rule 9 and token "*", resolved as shift.
Shift/Reduce error in state 15 between rule 9 and token "/", resolved as shift.
Shift/Reduce error in state 16 between rule 7 and token "+", resolved as shift.
Shift/Reduce error in state 16 between rule 7 and token "-", resolved as shift.
Shift/Reduce error in state 16 between rule 7 and token "*", resolved as shift.
Shift/Reduce error in state 16 between rule 7 and token "/", resolved as shift.
Shift/Reduce error in state 17 between rule 8 and token "+", resolved as shift.
Shift/Reduce error in state 17 between rule 8 and token "-", resolved as shift.
Shift/Reduce error in state 17 between rule 8 and token "*", resolved as shift.
Shift/Reduce error in state 17 between rule 8 and token "/", resolved as shift.
Shift/Reduce error in state 18 between rule 10 and token "+", resolved as shift.
Shift/Reduce error in state 18 between rule 10 and token "-", resolved as shift.
Shift/Reduce error in state 18 between rule 10 and token "*", resolved as shift.
Shift/Reduce error in state 18 between rule 10 and token "/", resolved as shift.
!done
````

Here is how to use it :
````
$ tclsh hoc1.tac.tcl
3+5*7
 = 38
t
 -- error
(2+67)/3
 = 23
````

At this stage operator priority is not handled by the grammar, as shown below :
````
$ tclsh hoc1.tac.tcl
5*7+3
 = 50
````
The interpreter parses `5*7+3` as `5*(7+3)` which evaluates to `50` instead of `38` which is the right result. 

## Stage 2

As in the book, this stage adds 26 variables (the letters a-z) and operator precedence. As a result, `5*7+3` now evaluates as `38`.
````
$ tclsh hoc2.tac.tcl
5*7+3
 = 38
````

Variables are quite handy :
````
$ tclsh hoc2.tac.tcl
a = 10
 = 10
b = 20
 = 20
a*b
 = 200
10*a
 = 100
a-23
 = -13
````

## Stage 3

Stage 3 adds arbitrary variable names and builtin math functions. A few math constants are defined at the beginning (PI, E, GAMMA, ...). As in stage 2 variables are kept in a global array. Builtins are functions from the `::tcl::mathfunc` namespace which is used by TCL for evaluation of `expr`. `make hoc3` builds this version of the interpreter.

Here is a sample session of `hoc3` demonstrating the new capabilities :
````
$ tclsh hoc3.tac.tcl
cos(PI)
 = -1.0
sin(PI/6)
 = 0.49999999999999994
PI-4*atan(1)
 = 0.0
E-exp(1)
 = 0.0
sqrt(2)
 = 1.4142135623730951
````

## Stage 4

Stage 4 is a reimplementation of stage 3 using the TCL bytecode engine.

**Work in progress**

