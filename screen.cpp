#include "screen.h"

Screen::Screen() : value_(0) {}

const char* Screen::Name() const {
    return "Screen";
}

void Screen::Reset() {
    value_ = 0;
}

void Screen::Tick() {
    // Ekran bu örnekte pasif.
}

void Screen::SetValue(uint32_t value) {
    value_ = value;
}

uint32_t Screen::GetValue() const {
    return value_;
}
