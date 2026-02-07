#pragma once

#include <array>
#include <cstdint>
#include <string>
#include "alu.h"
#include "bus.h"
#include "ram.h"
#include "rom.h"

// Basit instruction set.
enum class Opcode : uint8_t {
    NOP = 0,
    LOAD = 1,
    STORE = 2,
    ADD = 3,
    SUB = 4,
    JMP = 5,
    JZ = 6,
    HALT = 7
};

struct Instruction {
    Opcode opcode{Opcode::NOP};
    uint8_t reg{0};
    uint16_t imm{0};
};

class CPU {
public:
    CPU();

    void Reset();
    bool Step(const Bus& bus, ROM& rom, RAM& ram);

    uint32_t GetPC() const;
    uint32_t GetRegister(size_t index) const;
    bool IsZeroFlagSet() const;
    bool IsHalted() const;
    std::string LastInstructionText() const;

private:
    Instruction Decode(uint32_t raw, const Bus& bus) const;
    std::string ToText(const Instruction& instruction) const;

    std::array<uint32_t, 8> regs_;
    uint32_t pc_;
    bool zeroFlag_;
    bool halted_;
    ALU alu_;
    std::string lastInstructionText_;
};
