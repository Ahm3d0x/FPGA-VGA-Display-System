`timescale 1ns/1ps

module time_counter_tb;

    reg clk;
    reg frame_tick;
    integer fps = 5;

    wire [3:0] hours_tens;
    wire [3:0] hours_ones;
    wire [3:0] minutes_tens;
    wire [3:0] minutes_ones;
    wire [3:0] seconds_tens;
    wire [3:0] seconds_ones;

    time_counter #(
        .FRAMES_PER_SECOND(5)
    ) dut (
        .clk(clk),
        .frame_tick(frame_tick),

        .hours_tens(hours_tens),
        .hours_ones(hours_ones),

        .minutes_tens(minutes_tens),
        .minutes_ones(minutes_ones),

        .seconds_tens(seconds_tens),
        .seconds_ones(seconds_ones)
    );

    // Clock
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Monitor
    initial begin
        $timeformat(-9, 0, " ns", 6);
        $monitor("Time = %0t |frame_tick = %b | Current Time = %0d%0d:%0d%0d:%0d%0d",
                 $time,frame_tick,hours_tens, hours_ones, minutes_tens, minutes_ones, seconds_tens, seconds_ones);
    end

    // Test
    initial begin

        frame_tick = 0;

        #20;

        repeat (fps) begin
            @(posedge clk);
            frame_tick = 1;

            @(posedge clk);
            frame_tick = 0;
        end


        repeat (fps) begin
            @(posedge clk);
            frame_tick = 1;

            @(posedge clk);
            frame_tick = 0;
        end

        repeat (fps) begin
            @(posedge clk);
            frame_tick = 1;

            @(posedge clk);
            frame_tick = 0;
        end

        #20;

        $stop;
    end

endmodule