module VGA_Sync (
      input  wire clk,
    
    output wire [9:0] pixel_x,
    output wire [9:0] pixel_y,
    output wire       video_on,
    output wire       hsync,
    output wire       vsync
);
reg [9:0] HCOUNT = 0;
reg [9:0] VCOUNT = 0;

always @(posedge clk) begin
      if (HCOUNT == 799 )
         HCOUNT <= 0 ; 
      else 
        HCOUNT <= HCOUNT + 1 ;
 end

 always @(posedge clk) begin
   if (HCOUNT == 799 ) begin
      if (VCOUNT == 524 )
         VCOUNT <= 0 ; 
      else 
        VCOUNT <= VCOUNT + 1 ;
  end
 end

assign pixel_x = HCOUNT;
assign pixel_y = VCOUNT;
assign video_on = ((HCOUNT < 640) && (VCOUNT< 480));
assign hsync = !((HCOUNT >= 656) && (HCOUNT <= 751));
assign vsync = !((VCOUNT >= 490) && (VCOUNT <= 492));

endmodule