#pragma once

#include <cstdint>

#include "peripheral.h"

// Basit ekran/7-segment temsili:
// Değer hem ham sayı hem de hex string olarak gösterilebilir.
class Screen : public Peripheral {
public:
    Screen();

    const char* Name() const override;
    void Reset() override;
    void Tick() override;

    void SetValue(uint32_t value);
    uint32_t GetValue() const;

private:
    uint32_t value_;
};
