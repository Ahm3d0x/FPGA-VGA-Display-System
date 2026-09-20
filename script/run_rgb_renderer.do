# ==============================================================================
# ModelSim / QuestaSim Simulation Script (run_rgb_renderer.do)
# Testbench: rgb_renderer_tb
# Target: Fast console execution generating output PPM files without waves
# Execution on console: vsim -c -do run_rgb_renderer.do
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

# 3. Ensure the output directory exists
if {![file exists "../data/out"]} {
    file mkdir "../data/out"
}

# 4. Create or refresh the 'work' library inside 'build'
if {[file exists "work"]} {
    catch {vdel -lib work -all}
}
vlib work
vmap work work

# 5. Compile RTL modules and Testbench with SystemVerilog enabled
vlog -sv -work work ../rtl/graphics_engine.v
vlog -sv -work work ../rtl/image_rom.v
vlog -sv -work work ../rtl/rgb_renderer.v
vlog -sv -work work ../tb/rgb_renderer_tb.v

# 6. Launch simulation (optimized for fast execution, with Altera megafunctions library)
vsim -L altera_mf_ver work.rgb_renderer_tb

# 7. Run the full test sequence to generate all output images
run -all

# 8. Exit automatically if running in console/batch mode
if {[batch_mode]} {
    quit -f
}
