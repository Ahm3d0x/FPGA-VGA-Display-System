module rgb_renderer (
    input wire [9:0] pixel_x,
    input wire [9:0] pixel_y,
    input wire [3:0] shape_form,
    input wire       video_on,

    output wire red,
    output wire green,
    output wire blue
);

    wire g_red;
    wire g_green;
    wire g_blue;

    wire i_red;
    wire i_green;
    wire i_blue;


    // Graphics Engine
    graphics_engine graphics_inst (
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .video_on(video_on),
        .shape_select(shape_form[3:0]),
        .red(g_red),
        .green(g_green),
        .blue(g_blue)
    );


    // Image ROM
    image_rom image_inst (
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .shape_form(shape_form[3:0]),
        .red(i_red),
        .green(i_green),
        .blue(i_blue)
    );




    // Output MUX
    assign red =
        (shape_form >= 4'd11) ?
        i_red :
        g_red;

    assign green =
        (shape_form >= 4'd11) ?
        i_green :
        g_green;

    assign blue =
        (shape_form >= 4'd11) ?
        i_blue :
        g_blue;

endmodule