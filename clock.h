#pragma once

#include <cstdint>

class Clock {
public:
    void tick() { ++cycles_; }
    void reset() { cycles_ = 0; }

    uint64_t cycles() const { return cycles_; }

    void setPower(bool on) { powerOn_ = on; }
    bool powerOn() const { return powerOn_; }

    void assertReset(bool value) { resetLine_ = value; }
    bool resetLine() const { return resetLine_; }

private:
    uint64_t cycles_{0};
    bool powerOn_{true};
    bool resetLine_{false};
};
