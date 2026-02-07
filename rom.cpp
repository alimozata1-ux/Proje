#include "rom.h"

ROM::ROM(size_t size) : words_(size, 0) {}

uint32_t ROM::Read(uint32_t address) const {
    if (address >= words_.size()) {
        return 0;
    }
    return words_[address];
}

void ROM::Write(uint32_t address, uint32_t value) {
    if (address < words_.size()) {
        words_[address] = value;
    }
}

void ROM::LoadProgram(const std::vector<uint32_t>& data) {
    Reset();
    const size_t count = (data.size() < words_.size()) ? data.size() : words_.size();
    for (size_t i = 0; i < count; ++i) {
        words_[i] = data[i];
    }
}

void ROM::Reset() {
    for (auto& word : words_) {
        word = 0;
    }
}

size_t ROM::Size() const {
    return words_.size();
}
