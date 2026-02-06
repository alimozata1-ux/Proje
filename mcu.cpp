#include "mcu.h"

MCU::MCU() : cpu(), ram(128 * 1024), rom(128 * 1024), bus(), pins(16), clock(), timer(), intc(), uart() {}

void MCU::reset(uint32_t startAddress) {
    cpu.reset(startAddress);
    ram.reset();
    clock.reset();
    clock.assertReset(true);
    timer.reset();
    intc.clear();
    uart = {};
    for (std::size_t i = 0; i < pins.count(); ++i) {
        pins.setDirection(i, Pins::Direction::In);
        pins.write(i, false);
    }
    clock.assertReset(false);
}
