# Makefile for hoc series of calculator

TCL=tclsh
FICKLE=./fickle/fickle.tcl
TACCLE=./taccle.tcl

all: hoc1 hoc2 hoc3

hoc3: hoc3.fcl.tcl hoc3.tac.tcl
	@echo "!done"

hoc2: hoc2.fcl.tcl hoc2.tac.tcl
	@echo "!done"

hoc1: hoc1.fcl.tcl hoc1.tac.tcl
	@echo "!done"


%.fcl.tcl: %.fcl
	$(TCL) $(FICKLE) -o $@ $<

%.tac.tcl: %.tac
	$(TCL) $(TACCLE) -d -v -w -o $@ $<

clean:
	-rm -f *tcl *output

.PHONY: clean all hoc1 hoc2 hoc3 hoc4
