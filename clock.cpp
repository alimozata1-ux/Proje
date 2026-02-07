#include "clock.h"

Clock::Clock() : cycles_(0) {}

void Clock::Tick() {
    ++cycles_;
}

void Clock::Reset() {
    cycles_ = 0;
}

uint64_t Clock::Cycles() const {
    return cycles_;
}
