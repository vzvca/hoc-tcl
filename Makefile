# Makefile for hoc series of calculator

TCL=tclsh
FICKLE=./fickle/fickle.tcl
TACCLE=./taccle/taccle.tcl

all: hoc1 hoc2 hoc3 hoc4 hoc5 hoc6 hoc7

%.fcl.tcl: %.fcl
	$(TCL) $(FICKLE) -o $@ $<

%.tac.tcl: %.tac
	$(TCL) $(TACCLE) -d -v -w -o $@ $<

%: %.fcl.tcl %.tac.tcl
	tclsh tool/flatten.tcl $@.tac.tcl > $@
	chmod +x $@

clean:
	-rm -f *tcl *output

.PHONY: clean all
