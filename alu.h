#pragma once

#include <cstdint>

class ALU {
public:
    struct Result {
        uint32_t value{0};
        bool zero{false};
        bool carry{false};
    };

    Result add(uint32_t a, uint32_t b) const;
    Result sub(uint32_t a, uint32_t b) const;
};
