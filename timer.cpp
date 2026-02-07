#include "timer.h"

Timer::Timer()
    : enabled_(true), prescaler_(8), subTick_(0), counter_(0), interruptPending_(false) {}

const char* Timer::Name() const {
    return "Timer";
}

void Timer::Reset() {
    enabled_ = true;
    prescaler_ = 8;
    subTick_ = 0;
    counter_ = 0;
    interruptPending_ = false;
}

void Timer::Tick() {
    if (!enabled_) {
        return;
    }

    ++subTick_;
    if (subTick_ >= prescaler_) {
        subTick_ = 0;
        ++counter_;
        interruptPending_ = true;
    }
}

void Timer::SetEnabled(bool enabled) {
    enabled_ = enabled;
}

bool Timer::IsEnabled() const {
    return enabled_;
}

void Timer::SetPrescaler(uint32_t prescaler) {
    prescaler_ = (prescaler == 0) ? 1 : prescaler;
}

uint32_t Timer::GetPrescaler() const {
    return prescaler_;
}

bool Timer::IsInterruptPending() const {
    return interruptPending_;
}

void Timer::ClearInterrupt() {
    interruptPending_ = false;
}

uint64_t Timer::Counter() const {
    return counter_;
}
