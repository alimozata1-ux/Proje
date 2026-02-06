#pragma once

#include "bus.h"
#include "clock.h"
#include "cpu.h"
#include "pins.h"
#include "ram.h"
#include "rom.h"
#include <cstdint>

struct TimerPeripheral {
    uint32_t counter{0};
    void tick() { ++counter; }
    void reset() { counter = 0; }
};

struct InterruptController {
    bool pending{false};
    void clear() { pending = false; }
};

struct UARTPeripheral {
    uint8_t tx{0};
    uint8_t rx{0};
};

class MCU {
public:
    MCU();

    void reset(uint32_t startAddress = 0);

    CPU cpu;
    RAM ram;
    ROM rom;
    Bus bus;
    Pins pins;
    Clock clock;
    TimerPeripheral timer;
    InterruptController intc;
    UARTPeripheral uart;
};
