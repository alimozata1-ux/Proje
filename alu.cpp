#include "alu.h"

ALU::Result ALU::add(uint32_t a, uint32_t b) const {
    uint64_t wide = static_cast<uint64_t>(a) + static_cast<uint64_t>(b);
    Result r;
    r.value = static_cast<uint32_t>(wide & 0xFFFFFFFFu);
    r.zero = (r.value == 0);
    r.carry = (wide > 0xFFFFFFFFu);
    return r;
}

ALU::Result ALU::sub(uint32_t a, uint32_t b) const {
    Result r;
    r.value = a - b;
    r.zero = (r.value == 0);
    r.carry = (a < b);
    return r;
}
