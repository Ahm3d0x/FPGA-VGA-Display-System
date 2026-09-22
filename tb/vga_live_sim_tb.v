`timescale 1ns/1ps

module vga_live_sim_tb ();
    // ports
    integer file;
    integer x;
    integer y;

    reg clk;
    reg [9:0] pixel_x;
    reg [9:0] pixel_y;
    reg [3:0] shape_form;
    reg       video_on;

    wire red;
    wire green;
    wire blue;

    // Clock generator (50 MHz / 20ns period)
    always #10 clk = ~clk;

    // DUT
    rgb_renderer dut (
        .clk(clk),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .shape_form(shape_form),
        .video_on(video_on),
        .red(red),
        .green(green),
        .blue(blue)
    );

    // Task to generate PPM Image for current shape
    task generate_ppm;
        input [3:0] test_shape;
        input test_video_on;
        begin
            shape_form = test_shape;
            video_on   = test_video_on;
            pixel_x    = 10'd0;
            pixel_y    = 10'd0;
            @(posedge clk);

            file = $fopen($sformatf("../data/out/photo_%0d.ppm", test_shape), "w");
            if (file == 0) begin
                $display("ERROR: Cannot open output file!");
                $stop;
            end

            // PPM Header
            $fwrite(file, "P3\n");
            $fwrite(file, "640 480\n");
            $fwrite(file, "255\n");

            // Scan image
            for (y = 0; y < 525; y = y + 1) begin
                for (x = 0; x < 800; x = x + 1) begin
                    pixel_x = x;
                    pixel_y = y;
                    @(posedge clk);
                    #1;
                    if (x < 640 && y < 480 && video_on) begin
                        $fwrite(file, "%0d ", (red   === 1'b1) ? 255 : 0);
                        $fwrite(file, "%0d ", (green === 1'b1) ? 255 : 0);
                        $fwrite(file, "%0d ", (blue  === 1'b1) ? 255 : 0);
                        if (x == 639) $fwrite(file, "\n");
                    end
                end
            end
            $fclose(file);
            $display("Shape %0d -> PPM generated successfully!", test_shape);
        end
    endtask

    integer target_shape;
    integer sim_duration;
    integer frames_per_sec;
    integer total_frames_to_run;
    integer frame_idx;
    integer cmd_file;
    integer cmd_shape;
    integer cmd_stop;
    integer scan_res;

    // Interactive continuous simulation session block
    initial begin
        clk = 0;

        if (!$value$plusargs("SHAPE=%d", target_shape)) begin
            target_shape = 12;
        end

        if (!$value$plusargs("DURATION=%d", sim_duration)) begin
            sim_duration = 5; // default 5 seconds
        end

        if (!$value$plusargs("FRAMES=%d", frames_per_sec)) begin
            frames_per_sec = 60;
        end

        shape_form = target_shape[3:0];
        video_on   = 1'b1;

        $display("==================================================");
        $display("Starting Interactive VGA Simulation Session:");
        $display("  Initial Shape: %0d", target_shape);
        $display("  Duration:      %0d seconds (%0d frames)", sim_duration, sim_duration * frames_per_sec);
        $display("==================================================");

        // Generate initial frame
        generate_ppm(shape_form, 1'b1);

        total_frames_to_run = sim_duration * frames_per_sec;
        for (frame_idx = 0; (sim_duration == 0) || (frame_idx < total_frames_to_run); frame_idx = frame_idx + 1) begin
            // Wait for one full VGA frame
            wait (dut.time_inst.frame_tick);
            @(posedge clk);

            // Read command file if updated by Python GUI (shape switch or stop command)
            cmd_file = $fopen("../data/sim_cmd.txt", "r");
            if (cmd_file != 0) begin
                scan_res = $fscanf(cmd_file, "%d %d", cmd_shape, cmd_stop);
                $fclose(cmd_file);
                if (scan_res == 2) begin
                    if (cmd_stop == 1) begin
                        $display("[GUI_CMD] Stop request received at frame %0d", frame_idx);
                        frame_idx = total_frames_to_run; // terminate loop
                    end else if (cmd_shape != shape_form && cmd_shape >= 0 && cmd_shape <= 15) begin
                        $display("[GUI_CMD] Dynamic Shape Change: %0d -> %0d at frame %0d", shape_form, cmd_shape, frame_idx);
                        shape_form = cmd_shape[3:0];
                        generate_ppm(shape_form, 1'b1);
                    end
                end
            end

            // In digital clock mode, update output PPM every simulated second
            if (shape_form >= 12 && frames_per_sec > 0 && (frame_idx % frames_per_sec == 0) && frame_idx > 0) begin
                $display("[CLOCK_TICK] Simulated 1 second elapsed -> Updating PPM");
                generate_ppm(shape_form, 1'b1);
            end
        end

        // Final frame generation
        generate_ppm(shape_form, 1'b1);

        $display("====================================");
        $display("SIMULATION SESSION COMPLETED SUCCESSFULLY");
        $display("====================================");
        $stop;
    end
endmodule
