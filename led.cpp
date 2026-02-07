#include "led.h"

LED::LED(size_t count) : states_(count, false) {}

const char* LED::Name() const {
    return "LED";
}

void LED::Reset() {
    for (size_t i = 0; i < states_.size(); ++i) {
        states_[i] = false;
    }
}

void LED::Tick() {
    // LED birimi bu örnekte pasif.
}

void LED::SetFromBitMask(uint32_t mask) {
    for (size_t i = 0; i < states_.size(); ++i) {
        states_[i] = ((mask >> i) & 0x1u) != 0;
    }
}

bool LED::GetState(size_t index) const {
    if (index < states_.size()) {
        return states_[index];
    }
    return false;
}

size_t LED::Count() const {
    return states_.size();
}
