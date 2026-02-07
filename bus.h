#pragma once

#include <cstdint>

// Veri yolu genişliği: 16-bit veya 32-bit.
enum class BusWidth {
    Bit16 = 16,
    Bit32 = 32
};

class Bus {
public:
    Bus();

    void SetWidth(BusWidth width);
    BusWidth GetWidth() const;

    // Veriyi seçili genişliğe göre maskeleyerek döndürür.
    uint32_t ApplyWidthMask(uint32_t value) const;

private:
    BusWidth width_;
};
