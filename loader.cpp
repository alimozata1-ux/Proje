#include "loader.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <sstream>

namespace {
std::string ToUpper(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::toupper(c));
    });
    return value;
}

std::string ExtensionOf(const std::string& path) {
    const auto dot = path.find_last_of('.');
    if (dot == std::string::npos) {
        return "";
    }
    return ToUpper(path.substr(dot));
}
} // namespace

bool Loader::LoadFile(const std::string& path, ROM& rom, BusWidth width, std::string& errorMessage) {
    std::vector<uint32_t> program;
    const std::string ext = ExtensionOf(path);

    bool ok = false;
    if (ext == ".HEX") {
        ok = LoadHex(path, program, errorMessage);
    } else if (ext == ".BIN") {
        ok = LoadBin(path, program, width, errorMessage);
    } else if (ext == ".C") {
        ok = LoadC(path, program, width, errorMessage);
    } else {
        errorMessage = "Desteklenmeyen dosya uzantısı. (.c/.hex/.bin bekleniyor)";
        return false;
    }

    if (ok) {
        rom.LoadProgram(program);
    }
    return ok;
}

bool Loader::LoadHex(const std::string& path, std::vector<uint32_t>& out, std::string& errorMessage) {
    std::ifstream file(path);
    if (!file) {
        errorMessage = "HEX dosyası açılamadı.";
        return false;
    }

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }
        uint32_t value = 0;
        std::stringstream ss;
        ss << std::hex << line;
        ss >> value;
        out.push_back(value);
    }
    return true;
}

bool Loader::LoadBin(const std::string& path, std::vector<uint32_t>& out, BusWidth width, std::string& errorMessage) {
    std::ifstream file(path, std::ios::binary);
    if (!file) {
        errorMessage = "BIN dosyası açılamadı.";
        return false;
    }

    if (width == BusWidth::Bit16) {
        while (true) {
            uint16_t word = 0;
            file.read(reinterpret_cast<char*>(&word), sizeof(word));
            if (!file) break;
            out.push_back(static_cast<uint32_t>(word));
        }
    } else {
        while (true) {
            uint32_t word = 0;
            file.read(reinterpret_cast<char*>(&word), sizeof(word));
            if (!file) break;
            out.push_back(word);
        }
    }

    return true;
}

bool Loader::LoadC(const std::string& path, std::vector<uint32_t>& out, BusWidth width, std::string& errorMessage) {
    std::ifstream file(path);
    if (!file) {
        errorMessage = "C dosyası açılamadı.";
        return false;
    }

    // Eğitim amaçlı mini çevirici:
    // Her satır: OPCODE REG IMM
    // Örn: ADD 0 10
    std::string line;
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '/' || line[0] == '#') {
            continue;
        }

        std::stringstream ss(line);
        std::string mnemonic;
        uint32_t reg = 0;
        uint32_t imm = 0;

        ss >> mnemonic;
        mnemonic = ToUpper(mnemonic);
        if (mnemonic.empty()) {
            continue;
        }

        if (mnemonic == "HALT" || mnemonic == "NOP") {
            out.push_back(EncodeInstruction(mnemonic, 0, 0, width));
            continue;
        }

        if (!(ss >> reg >> imm)) {
            errorMessage = "C parser satırı çözümleyemedi: " + line;
            return false;
        }

        out.push_back(EncodeInstruction(mnemonic, reg, imm, width));
    }

    return true;
}

uint32_t Loader::EncodeInstruction(const std::string& mnemonic, uint32_t reg, uint32_t imm, BusWidth width) const {
    uint32_t opcode = 0;
    if (mnemonic == "LOAD") opcode = 1;
    else if (mnemonic == "STORE") opcode = 2;
    else if (mnemonic == "ADD") opcode = 3;
    else if (mnemonic == "SUB") opcode = 4;
    else if (mnemonic == "JMP") opcode = 5;
    else if (mnemonic == "JZ") opcode = 6;
    else if (mnemonic == "HALT") opcode = 7;
    else opcode = 0;

    if (width == BusWidth::Bit16) {
        return ((opcode & 0xFu) << 12) | ((reg & 0xFu) << 8) | (imm & 0xFFu);
    }
    return ((opcode & 0xFFu) << 24) | ((reg & 0xFFu) << 16) | (imm & 0xFFFFu);
}
