module VGA_Sync (
   input  wire clk,

    output wire [9:0] pixel_x,
    output wire [9:0] pixel_y,
    output wire       video_on,
    output wire       hsync,
    output wire       vsync
);
reg [9:0] HCOUNT = 10'b0;
reg [9:0] VCOUNT = 10'b0;

always @(posedge clk) begin
      if (HCOUNT == 10'd799 )
         HCOUNT <= 10'b0 ; 
      else 
        HCOUNT <= HCOUNT +10'd1;
 end

 always @(posedge clk) begin
   if (HCOUNT == 10'd799 ) begin
      if (VCOUNT == 10'd524 )
         VCOUNT <= 10'b0 ; 
      else 
        VCOUNT <= VCOUNT +10'd1;
  end
 end

assign pixel_x = HCOUNT;
assign pixel_y = VCOUNT;
assign video_on = ((HCOUNT < 10'd640) && (VCOUNT< 10'd480));
assign hsync = !((HCOUNT >= 10'd656) && (HCOUNT <= 10'd751));
assign vsync = !((VCOUNT >= 10'd490) && (VCOUNT <= 10'd491));

endmodule