#pragma once

#include <cstdint>
#include <vector>

class Pins {
public:
    enum class Direction : uint8_t { In = 0, Out = 1 };

    explicit Pins(std::size_t count = 16);

    void setDirection(std::size_t idx, Direction dir);
    Direction direction(std::size_t idx) const;

    void write(std::size_t idx, bool value);
    bool read(std::size_t idx) const;

    std::size_t count() const { return values_.size(); }

private:
    std::vector<Direction> directions_;
    std::vector<bool> values_;
};
