module image_rom (
    input wire [9:0] pixel_x,
    input wire [9:0] pixel_y,
    input wire [3:0] shape_form,
    output wire red,
    output wire green,
    output wire blue
);
    localparam WIDTH = 640;
    localparam HEIGHT = 480;
    localparam MEM_SIZE = WIDTH * HEIGHT;

    reg [2:0] mem [0:MEM_SIZE-1];
    wire [18:0] address;
    assign address = pixel_y * WIDTH + pixel_x;
    // assign address = 1842;

    always @(shape_form) begin
        if (shape_form >= 4'd11) begin
            $readmemb($sformatf("../data/in/photo_%0d.mem", shape_form), mem);
        end
    end
    assign red = mem[address][2];
    assign green = mem[address][1];
    assign blue = mem[address][0];

endmodule
