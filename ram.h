#pragma once

#include <cstddef>
#include <cstdint>
#include <vector>

class RAM {
public:
    // RAM boyutu "word" cinsindendir (1 word = 32-bit = 4 byte).
    // Güvenlik/ürün gereksinimi: toplam RAM en fazla 1MB olabilir.
    explicit RAM(size_t sizeWords = 1024);

    uint32_t Read(uint32_t address) const;
    void Write(uint32_t address, uint32_t value);
    void Reset();

    size_t Size() const;

    static constexpr size_t MaxBytes() { return 1024u * 1024u; } // 1MB
    static constexpr size_t MaxWords() { return MaxBytes() / sizeof(uint32_t); }

private:
    std::vector<uint32_t> cells_;
};
