#include "ram.h"

RAM::RAM(size_t sizeWords)
    : cells_((sizeWords > MaxWords()) ? MaxWords() : sizeWords, 0) {}

uint32_t RAM::Read(uint32_t address) const {
    if (address >= cells_.size()) {
        return 0;
    }
    return cells_[address];
}

void RAM::Write(uint32_t address, uint32_t value) {
    if (address < cells_.size()) {
        cells_[address] = value;
    }
}

void RAM::Reset() {
    for (auto& cell : cells_) {
        cell = 0;
    }
}

size_t RAM::Size() const {
    return cells_.size();
}
