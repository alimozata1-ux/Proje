#pragma once

#include <string>
#include <vector>

#include "bus.h"
#include "rom.h"

class Loader {
public:
    bool LoadFile(const std::string& path, ROM& rom, BusWidth width, std::string& errorMessage);

private:
    bool LoadHex(const std::string& path, std::vector<uint32_t>& out, std::string& errorMessage);
    bool LoadBin(const std::string& path, std::vector<uint32_t>& out, BusWidth width, std::string& errorMessage);
    bool LoadC(const std::string& path, std::vector<uint32_t>& out, BusWidth width, std::string& errorMessage);
    uint32_t EncodeInstruction(const std::string& mnemonic, uint32_t reg, uint32_t imm, BusWidth width) const;
};
