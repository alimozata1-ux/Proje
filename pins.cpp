#include "pins.h"

Pins::Pins(std::size_t count) : directions_(count, Direction::In), values_(count, false) {}

void Pins::setDirection(std::size_t idx, Direction dir) {
    if (idx >= directions_.size()) return;
    directions_[idx] = dir;
}

Pins::Direction Pins::direction(std::size_t idx) const {
    if (idx >= directions_.size()) return Direction::In;
    return directions_[idx];
}

void Pins::write(std::size_t idx, bool value) {
    if (idx >= values_.size()) return;
    values_[idx] = value;
}

bool Pins::read(std::size_t idx) const {
    if (idx >= values_.size()) return false;
    return values_[idx];
}
