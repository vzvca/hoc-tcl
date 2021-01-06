proc aproc {name argl body args} {
    proc $name $argl $body
    set res [disasm proc $name]
    if {"-x" in $args} {
        set res [list proc $name $argl [list asm [dis2asm $res]]]
        eval $res
    }
    return $res
}

 proc dis2asm body {
    set res ""
    set jumptargets {}
    foreach line [split $body \n] {
        if [regexp {\# pc (\d+)} $line -> pc] {lappend jumptargets $pc}
    }
    foreach line [split $body \n] {
        set line [string trim $line]
        if {$line eq ""} continue
        set code ""
        if {[regexp {\((\d+)\) (.+)} $line -> pc instr]} {
            if {$pc in $jumptargets} {
                append res "\n label L$pc;"
            }
            if {[regexp {(.+)#(.+)} $instr -> instr comment]} {
                set arg [lindex $comment end]
                if {$arg eq ""} {set arg "{}"}
                if [string match jump* $instr] {set arg L$arg}
            } else {set arg ""}
            set instr0 [normalize [lindex $instr 0]]
            if {$instr0 in {invokeStk}} {set arg [lindex $instr end]}
            if {$instr0 in {incrImm}} {set arg [list $arg [lindex $instr end]]}
            if {$instr0 in {list}} {set arg [lindex $instr end]}           ;# PZ: 'list' missing arg. added
            set code [format " %-24s" "$instr0 $arg"]
            if {$instr0 in {startCommand}} {set code ""}
            append res "\n  $code ;# [string trim $line]"
        }
    }
    append res \n
    return $res
 }

 proc normalize instr {
    regsub {\d+$} $instr "" instr ;# strip off trailing length indicator
    set instr [string map {
        loadScalar load   nop ""   storeScalar store
        incrScalar1Imm incrImm
    } $instr]
    return $instr
 }

 #interp alias {} asm    {} ::tcl::unsupported::assemble ;# worksn't - the [assemble] command isn't exported yet
 namespace eval   tcl::unsupported {namespace export assemble}
 namespace import tcl::unsupported::assemble
 rename assemble asm
 interp alias {} disasm {} ::tcl::unsupported::disassemble
