# ==============================================================================
# ModelSim / QuestaSim Simulation Script
# Project: VGA Graphics Engine
# Execution: Run from the 'script' directory: do run.do
# ==============================================================================

# 1. Close any running simulation
quit -sim

# 2. Switch working directory to 'build' so all generated files,
#    work libraries, logs stay inside 'build'
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

# Ensure result folder exists inside tb folder
if {![file exists "../tb/tb_result"]} {
    file mkdir "../tb/tb_result"
}

# 3. Create or refresh the 'work' library inside 'build'
if {[file exists "work"]} {
    catch {vdel -lib work -all}
}
vlib work
vmap work work

# 4. Compile RTL design files
vlog -work work ../rtl/graphics_engine.v

# 5. Compile Testbench
vlog -work work ../tb/graphics_engine_tb.v

# 6. Launch simulation
vsim -voptargs=+acc work.graphics_engine_tb

# 7. Add waveforms (for GUI mode)
add wave -r /*

# 8. Run the simulation until $stop
run -all

# 9. Zoom fit waves (for GUI mode)
catch {wave zoom full}
