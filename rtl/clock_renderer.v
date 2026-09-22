module clock_renderer (
    input video_on,
    input  [9:0] pixel_x,pixel_y,
    input  [3:0] hours_tens,hours_ones, minutes_tens, minutes_ones, seconds_tens, seconds_ones,
    output  red, green, blue
);
localparam  DIGIT_W = 50;
localparam  DIGIT_H = 90;
localparam  THICK   = 10;
localparam  Y0 = 195;
localparam  X_H10 = 120;
localparam  X_H01 = 180;
localparam  X_C1  = 238;
localparam  X_M10 = 260;
localparam  X_M01 = 320;
localparam  X_C2  = 378;
localparam  X_S10 = 400;
localparam  X_S01 = 460;

// {a,b,c,d,e,f,g}
function [6:0] digit_segments;
    input [3:0] d;
    begin
        case (d)
            4'd0: digit_segments = 7'b1111110;
            4'd1: digit_segments = 7'b0110000;
            4'd2: digit_segments = 7'b1101101;
            4'd3: digit_segments = 7'b1111001;
            4'd4: digit_segments = 7'b0110011;
            4'd5: digit_segments = 7'b1011011;
            4'd6: digit_segments = 7'b1011111;
            4'd7: digit_segments = 7'b1110000;
            4'd8: digit_segments = 7'b1111111;
            4'd9: digit_segments = 7'b1111011;
            default:
                digit_segments = 7'b0000000;
        endcase
    end
endfunction


function digit_pixel;
    input [3:0] d;
    input integer local_x;
    input integer local_y;
    reg [6:0] s;
    begin
        s = digit_segments(d);
        digit_pixel = 1'b0;
        if (s[6] && local_y < THICK && local_x >= 0 && local_x <DIGIT_W) digit_pixel = 1'b1; // a
        if (s[5] && local_x >=DIGIT_W-THICK && local_y >= 0 && local_y < (DIGIT_H/2 + THICK/2)) digit_pixel = 1'b1; // b
        if (s[4] && local_x >=DIGIT_W-THICK && local_y >= (DIGIT_H/2 - THICK/2) && local_y <DIGIT_H) digit_pixel = 1'b1; // c
        if (s[3] && local_y >= DIGIT_H-THICK && local_x >= 0 && local_x <DIGIT_W) digit_pixel = 1'b1; // d
        if (s[2] && local_x < THICK && local_y >= DIGIT_H/2 - THICK/2  && local_y <DIGIT_H) digit_pixel = 1'b1; // e
        if (s[1] && local_x < THICK && local_y >= 0 && local_y <DIGIT_H/2 + THICK/2) digit_pixel = 1'b1; // f
        if (s[0] && local_y >= (DIGIT_H/2-THICK/2) && local_y <  (DIGIT_H/2+THICK/2) && local_x >= 0 && local_x <DIGIT_W) digit_pixel = 1'b1; // g
    end
endfunction


reg clock_pixel;

always @(*) begin
    clock_pixel = 1'b0;
    if ((pixel_y >= Y0) && (pixel_y < Y0 + DIGIT_H)) begin
        if ((pixel_x >= X_H10) && (pixel_x < X_H10 + DIGIT_W)) // frist digit of hours
            clock_pixel = digit_pixel(hours_tens, pixel_x-X_H10, pixel_y-Y0);
        else if ((pixel_x >= X_H01) && (pixel_x < X_H01 + DIGIT_W)) // second digit of hours
            clock_pixel = digit_pixel(hours_ones, pixel_x-X_H01, pixel_y-Y0);
        else if ((pixel_x >= X_M10) && (pixel_x < X_M10 + DIGIT_W)) // frist digit of minutes
            clock_pixel = digit_pixel(minutes_tens, pixel_x-X_M10, pixel_y-Y0);
        else if ((pixel_x >= X_M01) && (pixel_x < X_M01 + DIGIT_W)) // second digit of minutes
            clock_pixel = digit_pixel(minutes_ones, pixel_x-X_M01, pixel_y-Y0);
        else if ((pixel_x >= X_S10) && (pixel_x < X_S10 + DIGIT_W)) // frist digit of seconds
            clock_pixel = digit_pixel(seconds_tens, pixel_x-X_S10, pixel_y-Y0);
        else if ((pixel_x >= X_S01) && (pixel_x < X_S01 + DIGIT_W)) // second digit of seconds
            clock_pixel = digit_pixel(seconds_ones, pixel_x-X_S01, pixel_y-Y0);

        else if ((seconds_ones[0] == 1'b0) && (pixel_x >= X_C1) && (pixel_x < X_C1+14) && (pixel_y >= Y0+25) && (pixel_y < Y0+38))// First colon
            clock_pixel = 1'b1;
        else if ((seconds_ones[0] == 1'b0) && (pixel_x >= X_C1) && (pixel_x < X_C1+14) && (pixel_y >= Y0+52) && (pixel_y < Y0+65))
            clock_pixel = 1'b1;
        
        else if ((seconds_ones[0] == 1'b0) && (pixel_x >= X_C2) && (pixel_x < X_C2+14) && (pixel_y >= Y0+25) && (pixel_y < Y0+38))// Second colon
            clock_pixel = 1'b1;
        else if ((seconds_ones[0] == 1'b0) && (pixel_x >= X_C2) && (pixel_x < X_C2+14) && (pixel_y >= Y0+52) && (pixel_y < Y0+65))
            clock_pixel = 1'b1;
    end

end


// Cyan = RGB 011
assign red   = video_on ? clock_pixel : 1'b0;
assign green = video_on ? clock_pixel : 1'b0;
assign blue  = video_on ? clock_pixel : 1'b0;

endmodule