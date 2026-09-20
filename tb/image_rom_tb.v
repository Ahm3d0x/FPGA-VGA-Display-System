`timescale 1ns/1ps

module image_rom_tb();

    reg clk;
    reg [9:0] pixel_x;
    reg [9:0] pixel_y;
    localparam photo_num = 0;
    wire red;
    wire green;
    wire blue;

    always #10 clk = ~clk;

    image_rom dut (
        .clk(clk),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .red(red),
        .green(green),
        .blue(blue)
    );

    initial begin
        clk = 0;

        // Pixel 0
        pixel_x = 0;
        pixel_y = 0;
        #10;

        $display(
            "Pixel (0,0) = %b%b%b",
            red, green, blue
        );

        // Pixel 1
        pixel_x = 1;
        pixel_y = 0;
        #10;

        $display(
            "Pixel (1,0) = %b%b%b",
            red, green, blue
        );

        // Pixel 640
        pixel_x = 0;
        pixel_y = 1;
        #10;

        $display(
            "Pixel (0,1) = %b%b%b",
            red, green, blue
        );

        $stop;

    end

endmodule