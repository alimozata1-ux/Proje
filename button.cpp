#include "button.h"

Button::Button(size_t count) : pressed_(count, false) {}

const char* Button::Name() const {
    return "Button";
}

void Button::Reset() {
    for (size_t i = 0; i < pressed_.size(); ++i) {
        pressed_[i] = false;
    }
}

void Button::Tick() {
    // Buton bu örnekte pasif.
}

void Button::SetPressed(size_t index, bool pressed) {
    if (index < pressed_.size()) {
        pressed_[index] = pressed;
    }
}

bool Button::IsPressed(size_t index) const {
    if (index < pressed_.size()) {
        return pressed_[index];
    }
    return false;
}

size_t Button::Count() const {
    return pressed_.size();
}
