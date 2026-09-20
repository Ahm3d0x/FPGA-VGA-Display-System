
module vga_top (
    input  wire       clk,
    input  wire [3:0] shape_form,

    output wire       red,
    output wire       green,
    output wire       blue,
    output wire       hsync,
    output wire       vsync
);

    wire [9:0] pixel_x;
    wire [9:0] pixel_y;
    wire       video_on;
    

    VGA_Sync async (
        .clk(clk),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .video_on(video_on),
        .hsync(hsync),
        .vsync(vsync)
    );

    rgb_renderer graphic (
        .clk(clk),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .shape_form(shape_form),
        .video_on(video_on),
        .red(red),
        .green(green),
        .blue(blue)
    );

endmodule
