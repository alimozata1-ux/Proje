#pragma once

#include <cstdint>

struct BusState {
    uint32_t addressBus{0};
    uint8_t dataBus{0};
    uint8_t controlBus{0};
};

class Bus {
public:
    void setAddress(uint32_t address) { state_.addressBus = address; }
    void setData(uint8_t data) { state_.dataBus = data; }
    void setControl(uint8_t control) { state_.controlBus = control; }

    const BusState& state() const { return state_; }

private:
    BusState state_;
};
