module rgb_renderer (
    input wire        clk,
    input wire [9:0] pixel_x,
    input wire [9:0] pixel_y,
    input wire [3:0] shape_form,
    input wire       video_on,

    output wire red,
    output wire green,
    output wire blue
);

    wire g_red, g_green, g_blue;
    wire i_red, i_green, i_blue;
    wire c_red, c_green, c_blue;
    wire frame_tick;




    // Graphics Engine
    graphics_engine graphics_inst (
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .video_on(video_on),
        .shape_select(shape_form),
        .red(g_red),
        .green(g_green),
        .blue(g_blue)
    );


    // Image ROM
    image_rom image_inst (
        .clk(clk),
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        // .shape_form(shape_form[3:0]),
        .red(i_red),
        .green(i_green),
        .blue(i_blue)
    );




// Time Counter

    assign frame_tick = (pixel_x == 10'd799) && (pixel_y == 10'd524);
    
    wire [3:0] hours_tens, hours_ones, minutes_tens, minutes_ones, seconds_tens, seconds_ones;

    time_counter time_inst (
        .clk(clk),
        .frame_tick(frame_tick),

        .hours_tens(hours_tens),
        .hours_ones(hours_ones),

        .minutes_tens(minutes_tens),
        .minutes_ones(minutes_ones),

        .seconds_tens(seconds_tens),
        .seconds_ones(seconds_ones)
    );


// Clock Renderer

clock_renderer clock_inst (
    .video_on(video_on),

    .pixel_x(pixel_x),
    .pixel_y(pixel_y),

    .hours_tens(hours_tens),
    .hours_ones(hours_ones),

    .minutes_tens(minutes_tens),
    .minutes_ones(minutes_ones),

    .seconds_tens(seconds_tens),
    .seconds_ones(seconds_ones),

    .red(c_red),
    .green(c_green),
    .blue(c_blue)
);



    assign red =
        (shape_form >= 4'd12) ? c_red :
        (shape_form >= 4'd11) ? i_red :
        g_red;

    assign green =
        (shape_form >= 4'd12) ? c_green :
        (shape_form >= 4'd11) ? i_green :
        g_green;

    assign blue =
        (shape_form >= 4'd12) ? c_blue :
        (shape_form >= 4'd11) ? i_blue :
        g_blue;

endmodule