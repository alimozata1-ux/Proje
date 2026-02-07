#include "mcu.h"

MCU::MCU() : bus_(), clock_(), cpu_(), ram_(1024), rom_(1024), pins_(16) {}

void MCU::Reset() {
    clock_.Reset();
    cpu_.Reset();
    ram_.Reset();
    rom_.Reset();
    pins_.Reset();
}

bool MCU::Tick() {
    clock_.Tick();
    return cpu_.Step(bus_, rom_, ram_);
}

Bus& MCU::GetBus() { return bus_; }
const Bus& MCU::GetBus() const { return bus_; }

Clock& MCU::GetClock() { return clock_; }
const Clock& MCU::GetClock() const { return clock_; }

CPU& MCU::GetCPU() { return cpu_; }
const CPU& MCU::GetCPU() const { return cpu_; }

RAM& MCU::GetRAM() { return ram_; }
const RAM& MCU::GetRAM() const { return ram_; }

ROM& MCU::GetROM() { return rom_; }
const ROM& MCU::GetROM() const { return rom_; }

Pins& MCU::GetPins() { return pins_; }
const Pins& MCU::GetPins() const { return pins_; }
