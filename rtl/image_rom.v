// module image_rom (
//     input  wire [9:0] pixel_x,
//     input  wire [9:0] pixel_y,
//     input  wire [3:0] shape_form,
//     output wire       red,
//     output wire       green,
//     output wire       blue
// );
//     localparam WIDTH = 640;
//     localparam HEIGHT = 480;
//     localparam MEM_SIZE = WIDTH * HEIGHT;
//
//     reg [2:0] mem [0:MEM_SIZE-1];
//     wire [18:0] address = pixel_y * WIDTH + pixel_x;
//
//     always @(shape_form) begin
//         if (shape_form >= 4'd11) begin
//             $readmemb($sformatf("../data/in/photo_%0d.mem", shape_form), mem);
//         end
//     end
//     assign red   = mem[address][2];
//     assign green = mem[address][1];
//     assign blue  = mem[address][0];
// endmodule

// ============================================================






// ============================================================
// Image stored in ROM
// Stored resolution : 320 x 240
// VGA output         : 640 x 480
//
// Each stored pixel = 3 bits
//   bit 2 = Red
//   bit 1 = Green
//   bit 0 = Blue
//`
// Each stored pixel is displayed as a 2x2 VGA pixel block.
// ============================================================


module image_rom (
    input  wire        clk,
    input  wire [9:0] pixel_x,
    input  wire [9:0] pixel_y,

    output wire       red,
    output wire       green,
    output wire       blue
);

    localparam IMG_WIDTH  = 320;
    localparam IMG_HEIGHT = 240;
    localparam IMG_DEPTH  = IMG_WIDTH * IMG_HEIGHT;

    wire [8:0] img_x;
    wire [7:0] img_y;

    assign img_x = pixel_x[9:1];
    assign img_y = pixel_y[8:1];

    // address = y * 320 + x
    // Range: 0 ... 76799
    wire [16:0] address;
    wire [2:0] q;

    assign address = (pixel_x < 10'd640 && pixel_y < 10'd480) ? (17'd320 * img_y) + img_x : 17'd0;

    altsyncram #(
        .operation_mode("ROM"),
        .width_a(3),
        .widthad_a(17),
        .numwords_a(76800),
        .outdata_reg_a("UNREGISTERED"),
        .address_aclr_a("NONE"),
        .outdata_aclr_a("NONE"),

        .init_file("../data/in/photo_11.mif"),
        .intended_device_family("Cyclone IV E"),
        .lpm_type("altsyncram")
    ) image_memory (
        .clock0(clk),
        .rden_a(1'b1),
        .address_a(address),
        .q_a(q),

        // No asynchronous clear
        .aclr0(1'b0),
        .aclr1(1'b0),
        .addressstall_a(1'b0),
        .byteena_a(1'b1),
        .data_a(3'b000), // Not used because this is ROM
        .wren_a(1'b0)
    );

    assign red   = q[2];
    assign green = q[1];
    assign blue  = q[0];

endmodule

