#pragma once

#include <vector>

// Pin durumu (basit dijital giriş/çıkış modeli)
class Pins {
public:
    explicit Pins(size_t count = 16);

    void Set(size_t index, bool value);
    bool Get(size_t index) const;
    size_t Count() const;
    void Reset();

private:
    std::vector<bool> pins_;
};
