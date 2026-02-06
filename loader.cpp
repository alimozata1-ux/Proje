#include "loader.h"
#include <algorithm>
#include <fstream>
#include <sstream>

bool Loader::loadBinFile(const std::string& path, std::vector<uint8_t>& out, std::string& error) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        error = "BIN dosyasi acilamadi.";
        return false;
    }

    out.assign(std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>());
    return true;
}

uint8_t Loader::hexByte(const std::string& s, std::size_t pos, bool& ok) {
    ok = false;
    if (pos + 2 > s.size()) return 0;
    auto part = s.substr(pos, 2);
    uint32_t v = 0;
    std::stringstream ss;
    ss << std::hex << part;
    ss >> v;
    if (ss.fail()) return 0;
    ok = true;
    return static_cast<uint8_t>(v & 0xFFu);
}

bool Loader::loadIntelHexFile(const std::string& path, std::vector<uint8_t>& out, std::string& error) {
    std::ifstream in(path);
    if (!in) {
        error = "HEX dosyasi acilamadi.";
        return false;
    }

    std::vector<uint8_t> image(128 * 1024, 0);
    uint32_t maxWritten = 0;
    std::string line;

    while (std::getline(in, line)) {
        if (line.empty()) continue;
        if (line[0] != ':') {
            error = "Gecersiz HEX satiri.";
            return false;
        }

        bool ok = false;
        uint8_t len = hexByte(line, 1, ok); if (!ok) { error = "HEX uzunluk hatasi"; return false; }
        uint8_t addrHi = hexByte(line, 3, ok); if (!ok) { error = "HEX adres hatasi"; return false; }
        uint8_t addrLo = hexByte(line, 5, ok); if (!ok) { error = "HEX adres hatasi"; return false; }
        uint8_t rectype = hexByte(line, 7, ok); if (!ok) { error = "HEX record hatasi"; return false; }
        uint16_t baseAddr = static_cast<uint16_t>((addrHi << 8) | addrLo);

        if (rectype == 0x01) break; // EOF
        if (rectype != 0x00) continue; // basit sürüm: sadece data record

        std::size_t expected = 9 + len * 2 + 2;
        if (line.size() < expected) {
            error = "HEX satiri eksik";
            return false;
        }

        for (uint8_t i = 0; i < len; ++i) {
            uint8_t b = hexByte(line, 9 + i * 2, ok);
            if (!ok) {
                error = "HEX data parse hatasi";
                return false;
            }
            uint32_t addr = static_cast<uint32_t>(baseAddr) + i;
            if (addr >= image.size()) {
                error = "HEX veri adresi ROM sinirini asti";
                return false;
            }
            image[addr] = b;
            maxWritten = std::max(maxWritten, addr + 1);
        }
    }

    out.assign(image.begin(), image.begin() + maxWritten);
    return true;
}
