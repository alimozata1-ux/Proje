#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

class RAM {
public:
    explicit RAM(std::size_t sizeBytes = 128 * 1024);

    bool write(uint32_t address, uint8_t value);
    bool read(uint32_t address, uint8_t &value) const;
    void reset();

    std::size_t size() const { return data_.size(); }
    const std::vector<uint8_t>& raw() const { return data_; }

private:
    std::vector<uint8_t> data_;
};
