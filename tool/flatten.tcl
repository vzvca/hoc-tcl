# --------------------------------------------------------------------------
#  Used to produce a single TCL file fro a TCL script sourcing other
#  files.
# --------------------------------------------------------------------------

proc source fname {
    __set fin [__open $fname r]
    __set data [__read $fin]
    __close $fin
    __puts "## ==========> source $fname  (start)"
    __eval $data
    __puts "## ==========> source $fname  (end)"
}

proc unknown args {
    __puts "$args"
}

foreach cmd {if while set array proc foreach puts eval open read close} {
    rename $cmd __$cmd
}

__puts "#! /usr/bin/env tclsh"
source $argv


