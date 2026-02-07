#pragma once

#include "bus.h"
#include "clock.h"
#include "cpu.h"
#include "pins.h"
#include "ram.h"
#include "rom.h"

// MCU: donanım bloklarını bir araya getiren model sınıfı.
class MCU {
public:
    MCU();

    void Reset();
    bool Tick();

    Bus& GetBus();
    const Bus& GetBus() const;

    Clock& GetClock();
    const Clock& GetClock() const;

    CPU& GetCPU();
    const CPU& GetCPU() const;

    RAM& GetRAM();
    const RAM& GetRAM() const;

    ROM& GetROM();
    const ROM& GetROM() const;

    Pins& GetPins();
    const Pins& GetPins() const;

private:
    Bus bus_;
    Clock clock_;
    CPU cpu_;
    RAM ram_;
    ROM rom_;
    Pins pins_;
};
