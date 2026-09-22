# ==============================================================================
# ModelSim / QuestaSim Live Simulation Script (run_live_sim.do)
# Testbench: vga_live_sim_tb
# ==============================================================================

quit -sim

set current_dir [pwd]
if {[file tail $current_dir] eq "script"} {
    cd ../build
} elseif {[file tail $current_dir] ne "build"} {
    if {[file exists "../build"]} {
        cd ../build
    } elseif {[file exists "build"]} {
        cd build
    }
}

if {![file exists "../data/out"]} {
    file mkdir "../data/out"
}
if {![file exists "../data/sim_cmd.txt"]} {
    set fp [open "../data/sim_cmd.txt" w]
    puts $fp "12 0"
    close $fp
}

if {![file exists "work"]} {
    vlib work
    vmap work work
}

vlog -sv -work work ../rtl/graphics_engine.v
vlog -sv -work work ../rtl/image_rom.v
vlog -sv -work work ../rtl/time_counter.v
vlog -sv -work work ../rtl/clock_renderer.v
vlog -sv -work work ../rtl/rgb_renderer.v
vlog -sv -work work ../tb/vga_live_sim_tb.v

vsim -L altera_mf_ver work.vga_live_sim_tb
run -all

if {[batch_mode]} {
    quit -f
}
