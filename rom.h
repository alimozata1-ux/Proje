#pragma once

#include <cstdint>
#include <vector>

class ROM {
public:
    explicit ROM(size_t size = 1024);

    uint32_t Read(uint32_t address) const;
    void Write(uint32_t address, uint32_t value);
    void LoadProgram(const std::vector<uint32_t>& data);
    void Reset();
    size_t Size() const;

private:
    std::vector<uint32_t> words_;
};
