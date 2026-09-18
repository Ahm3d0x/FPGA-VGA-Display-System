module  graphics_engine  (
    input  wire [9:0] pixel_x,
    input  wire [9:0] pixel_y,
    input  wire       video_on,
    input  wire [3:0] shape_select,
    output wire red,
    output wire green,
    output wire blue
);

reg [2:0] color_out;
reg signed [10:0] dx;
reg signed [10:0] dy;
assign red   = video_on ? color_out[2] : 1'b0;
assign green = video_on ? color_out[1] : 1'b0;
assign blue  = video_on ? color_out[0] : 1'b0;

always @(*) begin
    dx = $signed({1'b0, pixel_x}) - 11'sd320;
    dy = $signed({1'b0, pixel_y}) - 11'sd240;

    case(shape_select)
    
    4'd0: begin
        if (pixel_x >= 220&& pixel_x <= 420&& pixel_y >= 150 && pixel_y <= 300) begin
            color_out = 3'b111;
        end else begin
            color_out = 3'b000;
        end
    end
    4'd1:begin
        if (pixel_x >= 220&& pixel_x <= 420&& pixel_y >= 150 && pixel_y <= 300) begin
            color_out = 3'b011;
        end else begin
            color_out = 3'b000;
        end
    end
    4'd2:begin
        if (pixel_x >= 220&& pixel_x <= 420&& pixel_y >= 150 && pixel_y <= 300) begin
            color_out = 3'b001;
        end else begin
            color_out = 3'b000;
        end
    end
    4'd3:begin
        if (pixel_x >= 220&& pixel_x <= 420&& pixel_y >= 150 && pixel_y <= 300) begin
            color_out = 3'b110;
        end else begin
            color_out = 3'b000;
        end
    end
    4'd4: begin
        if (pixel_x <= 79)
            color_out = 3'b001;
        else if (pixel_x <= 159)
            color_out = 3'b010;
        else if (pixel_x <= 239)
            color_out = 3'b011;
        else if (pixel_x <= 319)
            color_out = 3'b100;
        else if (pixel_x <= 399)
            color_out = 3'b101;
        else if (pixel_x <= 479)
            color_out = 3'b110;
        else if (pixel_x <= 559)
            color_out = 3'b111;
        else
            color_out = 3'b000;
    end
    4'd5: begin
    if (pixel_y <= 59)
        color_out = 3'b001;
    else if (pixel_y <= 119)
        color_out = 3'b010;
    else if (pixel_y <= 179)
        color_out = 3'b011;
    else if (pixel_y <= 239)
        color_out = 3'b100;
    else if (pixel_y <= 299)
        color_out = 3'b101;
    else if (pixel_y <= 359)
        color_out = 3'b110;
    else if (pixel_y <= 419)
        color_out = 3'b111;
    else
        color_out = 3'b000;
    end
    4'd6: begin
        if((dx ) * (dx) + (dy) * (dy) <= 10000) begin // (x−h)2+(y−k)2=r2 
            color_out = 3'b111;
        end else begin
            color_out = 3'b000;
        end
    end
    4'd7: begin
        if((dx ) * (dx) + (dy) * (dy) <= 22500) begin 
            color_out = 3'b001;
        end else begin
            color_out = 3'b111;
        end
    end
    4'd8: begin

    if ((dx * dx) + (dy * dy) <= 22500) begin
        color_out = 3'b001;
    end else if (pixel_x >= 220 && pixel_x <= 420 && pixel_y >= 165 && pixel_y <= 315) begin
        color_out = 3'b111;
    end else begin
        color_out = 3'b000; 
    end

end
    4'd9: begin
        if((dx ) * (dx) + (dy) * (dy) <= 4000) color_out = 3'b111;
        else if((dx ) * (dx) + (dy) * (dy) <= 8000) color_out = 3'b000;
        else if((dx ) * (dx) + (dy) * (dy) <= 12000) color_out = 3'b111;
        else if((dx ) * (dx) + (dy) * (dy) <= 16000) color_out = 3'b000;
        else if((dx ) * (dx) + (dy) * (dy) <= 20000) color_out = 3'b111;
        else if((dx ) * (dx) + (dy) * (dy) <= 24000) color_out = 3'b111;
        else if((dx ) * (dx) + (dy) * (dy) <= 28000) color_out = 3'b000;
        else if((dx ) * (dx) + (dy) * (dy) <= 32000) color_out = 3'b111;
        else if((dx ) * (dx) + (dy) * (dy) <= 36000) color_out = 3'b000;
        else if((dx ) * (dx) + (dy) * (dy) <= 40000) color_out = 3'b111;
        else color_out = 3'b000;
    end
    4'd10: begin

        if((dx ) * (dx) + (dy) * (dy) <= 8000) color_out = 3'b000;
        else if((dx ) * (dx) + (dy) * (dy) <= 16000) color_out = 3'b001;
        else if((dx ) * (dx) + (dy) * (dy) <= 24000) color_out = 3'b010;
        else if((dx ) * (dx) + (dy) * (dy) <= 32000) color_out = 3'b011;
        else if((dx ) * (dx) + (dy) * (dy) <= 40000) color_out = 3'b100;
        else if((dx ) * (dx) + (dy) * (dy) <= 48000) color_out = 3'b101;
        else if((dx ) * (dx) + (dy) * (dy) <= 56000) color_out = 3'b110;
        else color_out = 3'b111;
        
    end  
    default:begin
        color_out = 3'b000;
    end
   
endcase

end





endmodule