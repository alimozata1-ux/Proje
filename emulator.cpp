#include "emulator.h"

#include <sstream>

Emulator::Emulator()
    : mcu_(), running_(false), led_(8), button_(8), screen_(), timer_() {
    mcu_.Reset();
}

bool Emulator::LoadProgram(const std::string& path, std::string& errorMessage) {
    const bool ok = loader_.LoadFile(path, mcu_.GetROM(), mcu_.GetBus().GetWidth(), errorMessage);
    if (ok) {
        mcu_.GetCPU().Reset();
        mcu_.GetClock().Reset();
        timer_.Reset();
    }
    return ok;
}

void Emulator::SetBusWidth(BusWidth width) {
    mcu_.GetBus().SetWidth(width);
    Reset();
}

BusWidth Emulator::GetBusWidth() const {
    return mcu_.GetBus().GetWidth();
}

void Emulator::Run() {
    running_ = true;
}

void Emulator::Pause() {
    running_ = false;
}

void Emulator::Reset() {
    running_ = false;
    mcu_.Reset();

    led_.Reset();
    button_.Reset();
    screen_.Reset();
    timer_.Reset();
}

void Emulator::Step() {
    timer_.Tick();

    if (mcu_.Tick()) {
        SyncButtonsToPins();
        UpdatePeripherals();
    } else {
        running_ = false;
    }
}

bool Emulator::IsRunning() const {
    return running_;
}

void Emulator::SetButtonState(size_t index, bool pressed) {
    button_.SetPressed(index, pressed);
    SyncButtonsToPins();
}

bool Emulator::GetLedState(size_t index) const {
    return led_.GetState(index);
}

uint32_t Emulator::GetScreenValue() const {
    return screen_.GetValue();
}

bool Emulator::IsTimerInterruptPending() const {
    return timer_.IsInterruptPending();
}

void Emulator::ClearTimerInterrupt() {
    timer_.ClearInterrupt();
}

std::string Emulator::GetStatusText() const {
    std::ostringstream oss;
    oss << "PC=" << mcu_.GetCPU().GetPC()
        << " CYC=" << mcu_.GetClock().Cycles()
        << " ZF=" << (mcu_.GetCPU().IsZeroFlagSet() ? "1" : "0")
        << " BUS=" << static_cast<int>(mcu_.GetBus().GetWidth())
        << " TINT=" << (timer_.IsInterruptPending() ? "1" : "0")
        << " LAST=" << mcu_.GetCPU().LastInstructionText();
    return oss.str();
}

void Emulator::UpdatePeripherals() {
    // RAM[0] -> LED bit alanı
    led_.SetFromBitMask(mcu_.GetRAM().Read(0));

    // RAM[1] -> basit ekran değeri
    screen_.SetValue(mcu_.GetRAM().Read(1));

    // RAM[2] -> timer prescaler register (örnek memory-mapped yapı)
    timer_.SetPrescaler(mcu_.GetRAM().Read(2));

    // Timer sayacı RAM[3]'e yansıtılır.
    mcu_.GetRAM().Write(3, static_cast<uint32_t>(timer_.Counter()));
}

void Emulator::SyncButtonsToPins() {
    const size_t count = (button_.Count() < mcu_.GetPins().Count()) ? button_.Count() : mcu_.GetPins().Count();
    for (size_t i = 0; i < count; ++i) {
        mcu_.GetPins().Set(i, button_.IsPressed(i));
    }
}
