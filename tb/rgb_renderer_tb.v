`timescale 1ns/1ps

module rgb_renderer_tb ();
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

// task to Generate PPM Image
    task generate_ppm;

        input [3:0] test_shape;
        input test_video_on;
        begin
            shape_form = test_shape;
            video_on   = test_video_on;
            pixel_x    = 10'd0;
            pixel_y    = 10'd0;
            @(posedge clk);

            // Open file
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
            // for (y = 0; y < 480; y = y + 1) begin
            //     for (x = 0; x < 640; x = x + 1) begin
            for (y = 0; y < 525; y = y + 1) begin
                for (x = 0; x < 800; x = x + 1) begin
                    pixel_x = x;
                    pixel_y = y;
                    @(posedge clk);
                    #1;
                    if (x < 640 && y < 480 && video_on) begin
                        // Write RGB (safeguarded against unknown/x values)
                        $fwrite(file, "%0d ", (red   === 1'b1) ? 255 : 0);
                        $fwrite(file, "%0d ", (green === 1'b1) ? 255 : 0);
                        $fwrite(file, "%0d ", (blue  === 1'b1) ? 255 : 0);
                        if (x == 639) $fwrite(file, "\n");
                    end
                end
            end
            // Close file
            $fclose(file);
            $display(
                "Shape %0d -> PPM generated successfully!",
                test_shape
            );
        end
    endtask



    // main test initial block
    initial begin
        clk = 0;
        // Test Graphics Engine
        generate_ppm(4'd0, 1'b1);
        generate_ppm(4'd1, 1'b1);
        generate_ppm(4'd2, 1'b1);
        generate_ppm(4'd3, 1'b1);
        generate_ppm(4'd4, 1'b1);
        generate_ppm(4'd5, 1'b1);
        generate_ppm(4'd6, 1'b1);
        generate_ppm(4'd7, 1'b1);
        generate_ppm(4'd8, 1'b1);
        generate_ppm(4'd9, 1'b1);
        generate_ppm(4'd10, 1'b1);
        // Test Image ROM
        generate_ppm(4'd11, 1'b1);
        // Test Clock Renderer
        generate_ppm(4'd12, 1'b1);
        $display("====================================");
        $display("ALL TESTS COMPLETED SUCCESSFULLY");
        $stop;
    end
endmodule
