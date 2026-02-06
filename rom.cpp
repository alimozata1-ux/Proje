#include "rom.h"
#include <algorithm>

ROM::ROM(std::size_t sizeBytes) : data_(sizeBytes, 0) {}

bool ROM::write(uint32_t address, uint8_t value) {
    if (address >= data_.size()) return false;
    data_[address] = value;
    return true;
}

bool ROM::read(uint32_t address, uint8_t &value) const {
    if (address >= data_.size()) return false;
    value = data_[address];
    return true;
}

void ROM::clear() {
    std::fill(data_.begin(), data_.end(), 0);
}

bool ROM::loadImage(const std::vector<uint8_t>& image, uint32_t startAddress) {
    if (startAddress > data_.size()) return false;
    if (image.size() > data_.size() - startAddress) return false;

    std::copy(image.begin(), image.end(), data_.begin() + startAddress);
    return true;
}
