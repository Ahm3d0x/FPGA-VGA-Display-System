# ==============================================================================
# ModelSim / QuestaSim Simulation Script (run_image_rom.do)
# Testbench: image_rom_tb
# Execution on console: vsim -c -do run_image_rom.do
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
vlog -sv -work work ../rtl/image_rom.v
vlog -sv -work work ../tb/image_rom_tb.v

# 5. Launch simulation
vsim -L altera_mf_ver -voptargs=+acc work.image_rom_tb

# 6. Run simulation until $stop (prints $display to the console)
run -all

# 7. Exit automatically if running in batch/console mode
if {[batch_mode]} {
    quit -f
}
