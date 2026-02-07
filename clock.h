#pragma once

#include <cstdint>

class Clock {
public:
    Clock();

    void Tick();
    void Reset();
    uint64_t Cycles() const;

private:
    uint64_t cycles_;
};
