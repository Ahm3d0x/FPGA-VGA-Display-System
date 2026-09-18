`timescale 1ns/1ps

module VGA_Sync_tb;

reg clk;

wire [9:0] pixel_x;
wire [9:0] pixel_y;
wire video_on;
wire hsync;
wire vsync;

VGA_Sync U1 (
    .clk(clk),
    .pixel_x(pixel_x),
    .pixel_y(pixel_y),
    .video_on(video_on),
    .hsync(hsync),
    .vsync(vsync)
);

always #5 clk = ~clk;

initial begin
    clk = 0;

    #4200000;

    $finish;
end

initial begin
    $monitor("Time=%0t | X=%0d | Y=%0d | video_on=%0b | hsync=%0b | vsync=%0b",
             $time, pixel_x, pixel_y, video_on, hsync, vsync);
end
endmodule
