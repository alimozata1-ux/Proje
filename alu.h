#pragma once

#include <cstdint>
#include "bus.h"

class ALU {
public:
    // Toplama işlemi, veri yolu genişliğine göre maskeleme yapar.
    uint32_t Add(uint32_t a, uint32_t b, const Bus& bus) const;

    // Çıkarma işlemi, veri yolu genişliğine göre maskeleme yapar.
    uint32_t Sub(uint32_t a, uint32_t b, const Bus& bus) const;
};
