#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

#include "peripheral.h"

// LED dizisi simülasyonu.
// Varsayılan olarak 8 LED içerir.
class LED : public Peripheral {
public:
    explicit LED(size_t count = 8);

    const char* Name() const override;
    void Reset() override;
    void Tick() override;

    void SetFromBitMask(uint32_t mask);
    bool GetState(size_t index) const;
    size_t Count() const;

private:
    std::vector<bool> states_;
};
