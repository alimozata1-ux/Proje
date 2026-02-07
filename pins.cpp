#include "pins.h"

Pins::Pins(size_t count) : pins_(count, false) {}

void Pins::Set(size_t index, bool value) {
    if (index < pins_.size()) {
        pins_[index] = value;
    }
}

bool Pins::Get(size_t index) const {
    if (index < pins_.size()) {
        return pins_[index];
    }
    return false;
}

size_t Pins::Count() const {
    return pins_.size();
}

void Pins::Reset() {
    for (size_t i = 0; i < pins_.size(); ++i) {
        pins_[i] = false;
    }
}
