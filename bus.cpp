#include "bus.h"

Bus::Bus() : width_(BusWidth::Bit16) {}

void Bus::SetWidth(BusWidth width) {
    width_ = width;
}

BusWidth Bus::GetWidth() const {
    return width_;
}

uint32_t Bus::ApplyWidthMask(uint32_t value) const {
    if (width_ == BusWidth::Bit16) {
        return value & 0xFFFFu;
    }
    return value;
}
