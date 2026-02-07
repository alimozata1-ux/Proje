#pragma once

#include <cstdint>

#include "peripheral.h"

// Basit timer + interrupt üretimi.
// prescaler adım sayısına ulaşıldığında interrupt pending set edilir.
class Timer : public Peripheral {
public:
    Timer();

    const char* Name() const override;
    void Reset() override;
    void Tick() override;

    void SetEnabled(bool enabled);
    bool IsEnabled() const;

    void SetPrescaler(uint32_t prescaler);
    uint32_t GetPrescaler() const;

    bool IsInterruptPending() const;
    void ClearInterrupt();

    uint64_t Counter() const;

private:
    bool enabled_;
    uint32_t prescaler_;
    uint32_t subTick_;
    uint64_t counter_;
    bool interruptPending_;
};
