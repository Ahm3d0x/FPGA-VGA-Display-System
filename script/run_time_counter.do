# ==============================================================================
# ModelSim / QuestaSim Simulation Script (run_time_counter.do)
# Testbench: time_counter_tb
# Execution on console: vsim -c -do run_time_counter.do
# ==============================================================================

# 1. Close any running simulation
quit -sim

# 2. Switch working directory to 'build'
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

# 3. Create or refresh the 'work' library inside 'build'
if {[file exists "work"]} {
    catch {vdel -lib work -all}
}
vlib work
vmap work work

# 4. Compile RTL and Testbench with SystemVerilog enabled
vlog -sv -work work ../rtl/time_counter.v
vlog -sv -work work ../tb/time_counter_tb.v

# 5. Launch simulation
vsim -voptargs=+acc work.time_counter_tb

# 6. Run simulation until $stop
run -all

# 7. Exit automatically if running in batch/console mode
if {[batch_mode]} {
    quit -f
}
