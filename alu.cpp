#include "alu.h"

uint32_t ALU::Add(uint32_t a, uint32_t b, const Bus& bus) const {
    return bus.ApplyWidthMask(a + b);
}

uint32_t ALU::Sub(uint32_t a, uint32_t b, const Bus& bus) const {
    return bus.ApplyWidthMask(a - b);
}
