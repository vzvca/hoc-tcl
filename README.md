# hoc-tcl
Port of hoc from "The Unix Programming Environment" book to TCL using taccle/fickle yacc/lex TCL clones.

Chapter 8 of the book by Brian W. Kernihgan & Rob Pike is devoted to program development. Along the chapter, the reader learns how to use yacc, lex and make, starting form a basic 4 functions interactive calculator and ending with a small but quite capable programming language including control flow and functions. This language is called hoc. 

There are 6 stages in hoc development with increasing complexity and functionality. Starting at stage 4 a bytecode engine is added, in this project I used the TCL builtin bytecode engine which is available at the script level using `::tcl::unsupported::assemble` since Tcl 8.6.3.

The 7th stage `hoc7` in this project adds some enhancements to the latest version described in the book. Most of the enhancements implemented here were left as exercises for the reader by the authors.

The code of `hoc7` is very small (less than 500 lines including blank lines and comments) and easy to understand.

This was just a fun project to understand how works TCL bytecode engine. But I find `hoc7` useful and use it as a calculator as a good alternative to `bc -l`.

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

Stage 4 is a reimplementation of stage 3 using the TCL bytecode engine. Let's replay stage 3 interactive session, same results : 

````
$ tclsh hoc4.tac.tcl
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

The bytecode is generated in a list kept in global variable `::todo`, bytecode instructions are pushed during parsing. Once a complete line has been parsed, the bytecode is assembled using `::tcl::unsupported::assemble` which evaluates it at the same time. The result is printed.

The bytecode generator is very crude and doesn't attempt to perform any optimization.

## Stage 5

Adding control flow `if ... else` and `while` loops. They get compiled to TCL bytecode and can be nested.

## Stage 6

Main improvements are procedure and functions. The compiler generates a TCL `proc` whose body is a `tcl::unsupported::assemble` statement. Like this :
````
func ftwo() { return 2*$1 }
````
becomes
````
proc ftwo args {
     lassign $args 1 2 3 4 5 6 7 8 9
     ::tcl::unsupported::assemble { push 2 ; load 1 ; mult }
}
````
which disassembles to :
````
% disasm proc ftwo
ByteCode 0x0x8000b3a70, refCt 1, epoch 18, interp 0x0x80000d230 (epoch 18)
  Source "\n     lassign $args 1 2 3 4 5 6 7 8 9\n     ::tcl::uns..."
  Cmds 2, src 99, inst 99, litObjs 1, aux 0, stkDepth 2, code/src 0.00
  Proc 0x0x8000e7340, refCt 1, args 1, compiled locals 10
      slot 0, scalar, arg, "args"
      slot 1, scalar, "1"
      slot 2, scalar, "2"
      slot 3, scalar, "3"
      slot 4, scalar, "4"
      slot 5, scalar, "5"
      slot 6, scalar, "6"
      slot 7, scalar, "7"
      slot 8, scalar, "8"
      slot 9, scalar, "9"
  Commands 2:
      1: pc 0-92, src 6-36        2: pc 93-97, src 43-97
  Command 1: "lassign $args 1 2 3 4 5 6 7 8 9..."
    (0) loadScalar1 %v0         # var "args"
    (2) dup
    (3) listIndexImm 0
    (8) storeScalar1 %v1        # var "1"
    (10) pop
    (11) dup
    (12) listIndexImm 1
    (17) storeScalar1 %v2       # var "2"
    (19) pop
    (20) dup
    (21) listIndexImm 2
    (26) storeScalar1 %v3       # var "3"
    (28) pop
    (29) dup
    (30) listIndexImm 3
    (35) storeScalar1 %v4       # var "4"
    (37) pop
    (38) dup
    (39) listIndexImm 4
    (44) storeScalar1 %v5       # var "5"
    (46) pop
    (47) dup
    (48) listIndexImm 5
    (53) storeScalar1 %v6       # var "6"
    (55) pop
    (56) dup
    (57) listIndexImm 6
    (62) storeScalar1 %v7       # var "7"
    (64) pop
    (65) dup
    (66) listIndexImm 7
    (71) storeScalar1 %v8       # var "8"
    (73) pop
    (74) dup
    (75) listIndexImm 8
    (80) storeScalar1 %v9       # var "9"
    (82) pop
    (83) listRangeImm 9 end
    (92) pop
  Command 2: "::tcl::unsupported::assemble { push 2 ; load 1 ; mult }..."
    (93) push1 0        # "2"
    (95) loadScalar1 %v1        # var "1"
    (97) mult
    (98) done
````

## Stage 7

The book stopped at hoc6 but suggest some enhancements like :
  * named function parameters (work-in-progress)
  * lazy evaluation like in C for `||` and `&&`  (done)
  * add `do ... while` loops  (done)
  * add `break` and `continue` to loops (done)
  * add C-like op-assign operators like `+=`, `-=` and so on (done)
  * add C-like `++` and `--` operators (done)
  * add C-like ternary operator `?:` (done)
  * add arrays and structured data
  * perform constant folding during expression compilation
  * add `~~` and `!~` operators to test if values are almost equals or not (using global EPS which defaults to 1e-6). (done)

These enhancements are being added to hoc7 with some internal changes :
  * global variables are not kept in the `::mem()` TCL array anymore.
  * in a function, each time a variable which is not a parameter is used it is assumed to be global and `upvar` is used.
  * the command `print` was removed, it is not needed since TCL `puts` can be used form hoc (like any other TCL command).
  * builtin string operations were added.
  * add a `var v1,v2, ...` statement to declare variables local to functions.

Structured data were implemented using `dict` and are using dedicated TCL bytecodes like `dictSet` and `dictGet`.


## TCL bytecodes

TCL bytecodes are not documented, what they do and how they are invoked has to be guessed by dissassembling code. The dissambler `tool/disasm.tcl` comes from the TCL wiki and helped a lot.

### Arithmetic opcodes

Arithmetic opcodes with 2 arguments are `add`, `sub`, `mult`, `div`, `mod` and `expon`. They operates on the two values on the top of the stack, first operand being at [stack-1] and second operand at [stack].

Unary opcode `uminus` negates top of stack. `push 1 ; uminus` leaves `-1` on top of stack.

### Variables

Code for upvar `push 1 ; push y ; upvar x` will create a procedure local variable `x` which is an alias for `y`.

Code `load x` will push procedure local variable `x` value on the stack.

Code `store x` will store value on top of stack in procedure local variable `x`

Code `push ::x ; loadStk` will work for global variables.

Code `push field1 ; push field2 ; push value ; dictSet 1 dico` will update procedure local dictionnary held in `dico`. Like `dict set dico field1 field2 value`.

Code `load dico ; push field1 ; push field2 ; dictGet 2` will push on stack the result of `dict get $dico field1 field2`.


### Control Flow

Control flow statements are implemented with jumps (conditional or not) and labels. Jump instructions are
  * `jumpFalse label` : pops top value of stack, if 0 jumps to label otherwise proceeds to next instruction.
  * `jumpTrue label`: pops top value of stack, if NOT 0 jumps to label otherwise proceeds to next instruction.
  * `jump label` : always jump, doesn't change the stack. Used to implement `return`.


## Future directions

Maybe I will try a reimplementation of `little language` using `fickle/tackle`.


