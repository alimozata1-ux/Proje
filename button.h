#pragma once

#include <cstddef>
#include <vector>

#include "peripheral.h"

// Dijital buton (giriş) simülasyonu.
class Button : public Peripheral {
public:
    explicit Button(size_t count = 8);

    const char* Name() const override;
    void Reset() override;
    void Tick() override;

    void SetPressed(size_t index, bool pressed);
    bool IsPressed(size_t index) const;
    size_t Count() const;

private:
    std::vector<bool> pressed_;
};
