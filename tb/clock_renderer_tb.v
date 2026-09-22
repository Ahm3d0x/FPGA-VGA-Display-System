

`timescale 1ns/1ps

module clock_renderer_tb;

    reg        video_on;
    reg [9:0]  pixel_x;
    reg [9:0]  pixel_y;

    reg [3:0] hours_tens;
    reg [3:0] hours_ones;
    reg [3:0] minutes_tens;
    reg [3:0] minutes_ones;
    reg [3:0] seconds_tens;
    reg [3:0] seconds_ones;

    wire red;
    wire green;
    wire blue;
    integer file;

    clock_renderer DUT (
        .video_on(video_on),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),

        .hours_tens(hours_tens),
        .hours_ones(hours_ones),
        .minutes_tens(minutes_tens),
        .minutes_ones(minutes_ones),
        .seconds_tens(seconds_tens),
        .seconds_ones(seconds_ones),

        .red(red),
        .green(green),
        .blue(blue)
    );

    integer x;
    integer y;

    initial begin

        video_on = 1'b1;

        hours_tens   = 4'd0;
        hours_ones   = 4'd1;
        minutes_tens = 4'd2;
        minutes_ones = 4'd3;
        seconds_tens = 4'd4;
        seconds_ones = 4'd5;

        // Start outside display area
        pixel_x = 0;
        pixel_y = 0;

        #10;

        $display("        CLOCK RENDERER ASCII TEST");
        $display("======================================");
        $display("");

            file = $fopen($sformatf("../data/out/clock.ppm"), "w");
            if (file == 0) begin
                $display("ERROR: Cannot open output file!");
                $stop;
            end

            $fwrite(file, "P3\n");
            $fwrite(file, "640 480\n");
            $fwrite(file, "255\n");

            for (y = 0; y < 480; y = y + 1) begin
                for (x = 0; x < 640; x = x + 1) begin
                    pixel_x = x;
                    pixel_y = y;
                    // @(posedge clk);
                    #1;
                    $fwrite(file, "%0d ", (red   === 1'b1) ? 255 : 0);
                    $fwrite(file, "%0d ", (green === 1'b1) ? 255 : 0);
                    $fwrite(file, "%0d ", (blue  === 1'b1) ? 255 : 0);
                end
                $fwrite(file, "\n");
            end
            $fclose(file);
        $display("Image saved to data\\out\\clock.ppm");
        
        $display("======================================");

        $stop;
    end

endmodule