#include "ram.h"
#include <algorithm>

RAM::RAM(std::size_t sizeBytes) : data_(sizeBytes, 0) {}

bool RAM::write(uint32_t address, uint8_t value) {
    if (address >= data_.size()) return false;
    data_[address] = value;
    return true;
}

bool RAM::read(uint32_t address, uint8_t &value) const {
    if (address >= data_.size()) return false;
    value = data_[address];
    return true;
}

void RAM::reset() {
    std::fill(data_.begin(), data_.end(), 0);
}
