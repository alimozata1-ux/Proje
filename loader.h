#pragma once

#include <cstdint>
#include <string>
#include <vector>

class Loader {
public:
    bool loadBinFile(const std::string& path, std::vector<uint8_t>& out, std::string& error);
    bool loadIntelHexFile(const std::string& path, std::vector<uint8_t>& out, std::string& error);

private:
    static uint8_t hexByte(const std::string& s, std::size_t pos, bool& ok);
};
