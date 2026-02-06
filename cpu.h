#pragma once

#include "alu.h"
#include "bus.h"
#include "ram.h"
#include "rom.h"
#include <array>
#include <cstdint>
#include <string>

class CPU {
public:
    enum class Opcode : uint8_t {
        NOP = 0x00,
        LOAD = 0x10,
        STORE = 0x11,
        ADD = 0x20,
        SUB = 0x21,
        JMP = 0x30,
        JZ = 0x31,
        HALT = 0xFF
    };

    struct Instruction {
        Opcode opcode{Opcode::NOP};
        uint8_t a{0};
        uint8_t b{0};
        uint8_t c{0};
    };

    CPU();

    void reset(uint32_t startAddress = 0);
    bool step(ROM& rom, RAM& ram, Bus& bus);

    uint32_t pc() const { return pc_; }
    bool halted() const { return halted_; }
    bool zeroFlag() const { return zeroFlag_; }

    const std::array<uint32_t, 8>& registers() const { return regs_; }
    Instruction lastInstruction() const { return lastInst_; }
    std::string lastInstructionText() const;

private:
    Instruction fetch(ROM& rom, Bus& bus);
    static uint16_t makeAddress(uint8_t hi, uint8_t lo);

    ALU alu_;
    std::array<uint32_t, 8> regs_{};
    uint32_t pc_{0};
    bool zeroFlag_{false};
    bool halted_{false};
    Instruction lastInst_{};
};
