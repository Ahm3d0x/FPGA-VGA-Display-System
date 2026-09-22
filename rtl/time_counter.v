module time_counter #(
    parameter integer FRAMES_PER_SECOND = 60
) (
    input  wire       clk,
    input  wire       frame_tick,
    output reg [3:0] hours_tens,
    output reg [3:0] hours_ones,
    output reg [3:0] minutes_tens,
    output reg [3:0] minutes_ones,
    output reg [3:0] seconds_tens,
    output reg [3:0] seconds_ones
);
reg [5:0] frame_count;
initial begin
    frame_count  = 6'd0;
    hours_tens   = 4'd0;
    hours_ones   = 4'd0;
    minutes_tens = 4'd0;
    minutes_ones = 4'd0;
    seconds_tens = 4'd0;
    seconds_ones = 4'd0;
end
always @(posedge clk) begin
    if (frame_tick) begin
        if (frame_count == FRAMES_PER_SECOND - 1) begin
            frame_count <= 6'd0;
            if (seconds_ones == 4'd9) begin seconds_ones <= 4'd0;
                if (seconds_tens == 4'd5) begin  seconds_tens <= 4'd0;
                    if (minutes_ones == 4'd9) begin minutes_ones <= 4'd0;
                        if (minutes_tens == 4'd5) begin minutes_tens <= 4'd0;

                            if ((hours_tens == 4'd2) && (hours_ones == 4'd3)) begin hours_tens <= 4'd0; hours_ones <= 4'd0; end
                            else if (hours_ones == 4'd9) begin hours_ones <= 4'd0; hours_tens <= hours_tens + 4'd1; end
                            else begin hours_ones <= hours_ones + 4'd1; end

                        end else begin minutes_tens <= minutes_tens + 4'd1; end
                    end else begin minutes_ones <= minutes_ones + 4'd1; end
                end else begin seconds_tens <= seconds_tens + 4'd1; end
            end else begin seconds_ones <= seconds_ones + 4'd1; end
        end else begin frame_count <= frame_count + 6'd1; end
    end
end
endmodule