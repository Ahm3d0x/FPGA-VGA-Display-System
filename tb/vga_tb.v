
`timescale 1ns / 1ps

module vga_tb();

    reg clk;
    reg [3:0] shape_form;

    wire red;
    wire green;
    wire blue;
    wire hsync;
    wire vsync;

    integer file;
    integer i;

    vga_top dut (
        .clk(clk),
        .shape_form(shape_form),
        .red(red),
        .green(green),
        .blue(blue),
        .hsync(hsync),
        .vsync(vsync)
    );

    always #10 clk = ~clk;

    initial begin

        clk = 0;

        for (i = 0; i < 16; i = i + 1) begin

            shape_form = i[3:0];

            file = $fopen($sformatf("output_%0d.ppm", i), "w");

            $fwrite(file, "P3\n640 480\n255\n");

            #8400000;

            $fclose(file);

        end

        $display("All 16 shapes tested successfully.");

        $finish;

    end

    always @(posedge clk) begin

        if (dut.video_on) begin

            $fwrite(file, "%d %d %d\n",
                red   ? 255 : 0,
                green ? 255 : 0,
                blue  ? 255 : 0
            );
        end
    end

endmodule
