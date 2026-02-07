#pragma once

#include <cstddef>
#include <string>

#include "button.h"
#include "led.h"
#include "loader.h"
#include "mcu.h"
#include "screen.h"
#include "timer.h"

// Emulator: Controller katmanı.
// GUI'den gelen komutları modele uygular.
class Emulator {
public:
    Emulator();

    bool LoadProgram(const std::string& path, std::string& errorMessage);

    void SetBusWidth(BusWidth width);
    BusWidth GetBusWidth() const;

    void Run();
    void Pause();
    void Reset();
    void Step();

    bool IsRunning() const;

    // LED/Button/Screen simülasyonu
    void SetButtonState(size_t index, bool pressed);
    bool GetLedState(size_t index) const;
    uint32_t GetScreenValue() const;

    bool IsTimerInterruptPending() const;
    void ClearTimerInterrupt();

    std::string GetStatusText() const;

private:
    void UpdatePeripherals();
    void SyncButtonsToPins();

    MCU mcu_;
    Loader loader_;
    bool running_;

    LED led_;
    Button button_;
    Screen screen_;
    Timer timer_;
};
