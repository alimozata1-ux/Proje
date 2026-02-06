#pragma once

#include "loader.h"
#include "mcu.h"
#include <cstdint>
#include <string>

class Emulator {
public:
    Emulator();

    bool loadProgramBin(const std::string& path, uint32_t startAddress, std::string& error);
    bool loadProgramHex(const std::string& path, uint32_t startAddress, std::string& error);

    void reset(uint32_t startAddress = 0);
    void run(bool value) { running_ = value; }
    void pause() { running_ = false; }
    bool isRunning() const { return running_; }

    bool step();
    void tickFrame(uint32_t maxCycles);

    MCU& mcu() { return mcu_; }
    const MCU& mcu() const { return mcu_; }

    uint32_t startAddress() const { return startAddress_; }

private:
    bool loadImageToRom(const std::vector<uint8_t>& image, uint32_t startAddress, std::string& error);

    MCU mcu_;
    Loader loader_;
    bool running_{false};
    uint32_t startAddress_{0};
};
