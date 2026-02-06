#include "emulator.h"

Emulator::Emulator() : mcu_(), loader_() {
    reset(0);
}

bool Emulator::loadImageToRom(const std::vector<uint8_t>& image, uint32_t startAddress, std::string& error) {
    if (startAddress >= mcu_.rom.size()) {
        error = "Baslangic adresi ROM disinda.";
        return false;
    }
    if (image.size() > mcu_.rom.size() - startAddress) {
        error = "Program boyutu ROM kapasitesini asiyor.";
        return false;
    }

    mcu_.rom.clear();
    if (!mcu_.rom.loadImage(image, startAddress)) {
        error = "ROM yukleme basarisiz.";
        return false;
    }

    startAddress_ = startAddress;
    mcu_.cpu.reset(startAddress_);
    return true;
}

bool Emulator::loadProgramBin(const std::string& path, uint32_t startAddress, std::string& error) {
    std::vector<uint8_t> image;
    if (!loader_.loadBinFile(path, image, error)) return false;
    return loadImageToRom(image, startAddress, error);
}

bool Emulator::loadProgramHex(const std::string& path, uint32_t startAddress, std::string& error) {
    std::vector<uint8_t> image;
    if (!loader_.loadIntelHexFile(path, image, error)) return false;
    return loadImageToRom(image, startAddress, error);
}

void Emulator::reset(uint32_t startAddress) {
    running_ = false;
    startAddress_ = startAddress;
    mcu_.reset(startAddress);
}

bool Emulator::step() {
    if (!mcu_.clock.powerOn()) return false;

    bool alive = mcu_.cpu.step(mcu_.rom, mcu_.ram, mcu_.bus);
    mcu_.clock.tick();
    mcu_.timer.tick();

    for (std::size_t i = 0; i < mcu_.pins.count(); ++i) {
        // Demo: alt bitleri pin durumuna bağla.
        bool v = ((mcu_.cpu.registers()[0] >> i) & 0x1u) != 0;
        mcu_.pins.write(i, v);
    }

    if (!alive) running_ = false;
    return alive;
}

void Emulator::tickFrame(uint32_t maxCycles) {
    if (!running_) return;
    for (uint32_t i = 0; i < maxCycles && running_; ++i) {
        if (!step()) break;
    }
}
