`timescale 1ns/1ps

// module graphics_engine_tb();

//     localparam SHAPE_FORM = 6;

//     reg [9:0] pixel_x;
//     reg [9:0] pixel_y;
//     reg       video_on;

//     wire red;
//     wire green;
//     wire blue;

//     graphics_engine #(
//         .SHAPE_FORM(SHAPE_FORM)
//     ) dut (
//         .pixel_x(pixel_x),
//         .pixel_y(pixel_y),
//         .video_on(video_on),
//         .red(red),
//         .green(green),
//         .blue(blue)
//     );

//     initial begin

//         video_on = 1'b1;

//         // Center of circle
//         pixel_x = 320;
//         pixel_y = 240;
//         #10;

//         // Outside circle
//         pixel_x = 0;
//         pixel_y = 0;
//         #10;

//         // Inside circle
//         pixel_x = 400;
//         pixel_y = 240;
//         #10;

//         // Outside circle
//         pixel_x = 421;
//         pixel_y = 240;
//         #10;

//         // Video OFF
//         video_on = 1'b0;
//         pixel_x = 320;
//         pixel_y = 240;
//         #10;

//         $stop;

//     end

// endmodule


//////////////////////////////////////////////////
//////////////////////////////////////////////////
//////////////////////////////////////////////////



module graphics_engine_tb();

    localparam SHAPE_FORM =8;

    reg [9:0] pixel_x;
    reg [9:0] pixel_y;
    reg       video_on;

    wire red;
    wire green;
    wire blue;

    integer x;
    integer y;
    integer file;

    graphics_engine #(
        .SHAPE_FORM(SHAPE_FORM)
    ) dut (
        .pixel_x(pixel_x),
        .pixel_y(pixel_y),
        .video_on(video_on),
        .red(red),
        .green(green),
        .blue(blue)
    );

    initial begin

        file = $fopen("../data/out/photo_"+$sformatf("%0d", SHAPE_FORM)+".ppm", "w");
        if (file == 0) begin
            file = $fopen("../data/out/photo_"+$sformatf("%0d", SHAPE_FORM)+".ppm", "w");
        end
        // PPM Header
        $fwrite(file, "P3\n");
        $fwrite(file, "640 480\n");
        $fwrite(file, "255\n");

        video_on = 1'b1;

        for (y = 0; y < 480; y = y + 1) begin

            for (x = 0; x < 640; x = x + 1) begin

                pixel_x = x;
                pixel_y = y;

                #1;

                // Red
                $fwrite(file, "%0d ", red * 255);

                // Green
                $fwrite(file, "%0d ", green * 255);

                // Blue
                $fwrite(file, "%0d ", blue * 255);

            end

            $fwrite(file, "\n");

        end

        $fclose(file);

        $display("PPM image generated successfully!");

        $stop;

    end

endmodule