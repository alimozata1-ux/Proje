#include "cpu.h"

#include <sstream>

CPU::CPU() : regs_{}, pc_(0), zeroFlag_(false), halted_(false), lastInstructionText_("NOP") {}

void CPU::Reset() {
    regs_.fill(0);
    pc_ = 0;
    zeroFlag_ = false;
    halted_ = false;
    lastInstructionText_ = "RESET";
}

Instruction CPU::Decode(uint32_t raw, const Bus& bus) const {
    Instruction i;
    if (bus.GetWidth() == BusWidth::Bit16) {
        // 16-bit format: [15:12 opcode][11:8 reg][7:0 imm]
        const uint16_t raw16 = static_cast<uint16_t>(raw & 0xFFFFu);
        i.opcode = static_cast<Opcode>((raw16 >> 12) & 0x0Fu);
        i.reg = static_cast<uint8_t>((raw16 >> 8) & 0x0Fu);
        i.imm = static_cast<uint16_t>(raw16 & 0x00FFu);
    } else {
        // 32-bit format: [31:24 opcode][23:16 reg][15:0 imm]
        i.opcode = static_cast<Opcode>((raw >> 24) & 0xFFu);
        i.reg = static_cast<uint8_t>((raw >> 16) & 0xFFu);
        i.imm = static_cast<uint16_t>(raw & 0xFFFFu);
    }
    return i;
}

std::string CPU::ToText(const Instruction& instruction) const {
    const int reg = instruction.reg % static_cast<int>(regs_.size());
    std::ostringstream oss;
    switch (instruction.opcode) {
    case Opcode::LOAD: oss << "LOAD R" << reg << ", [" << instruction.imm << "]"; break;
    case Opcode::STORE: oss << "STORE R" << reg << ", [" << instruction.imm << "]"; break;
    case Opcode::ADD: oss << "ADD R" << reg << ", [" << instruction.imm << "]"; break;
    case Opcode::SUB: oss << "SUB R" << reg << ", [" << instruction.imm << "]"; break;
    case Opcode::JMP: oss << "JMP " << instruction.imm; break;
    case Opcode::JZ: oss << "JZ " << instruction.imm; break;
    case Opcode::HALT: oss << "HALT"; break;
    default: oss << "NOP"; break;
    }
    return oss.str();
}

bool CPU::Step(const Bus& bus, ROM& rom, RAM& ram) {
    if (halted_) {
        return false;
    }

    const uint32_t raw = rom.Read(pc_);
    const Instruction instruction = Decode(raw, bus);
    lastInstructionText_ = ToText(instruction);

    const uint32_t r = instruction.reg % static_cast<uint32_t>(regs_.size());
    const uint32_t addr = instruction.imm;
    const uint32_t operand = bus.ApplyWidthMask(ram.Read(addr));

    switch (instruction.opcode) {
    case Opcode::LOAD:
        regs_[r] = bus.ApplyWidthMask(ram.Read(addr));
        zeroFlag_ = (regs_[r] == 0);
        ++pc_;
        break;
    case Opcode::STORE:
        ram.Write(addr, bus.ApplyWidthMask(regs_[r]));
        ++pc_;
        break;
    case Opcode::ADD:
        regs_[r] = alu_.Add(regs_[r], operand, bus);
        zeroFlag_ = (regs_[r] == 0);
        ++pc_;
        break;
    case Opcode::SUB:
        regs_[r] = alu_.Sub(regs_[r], operand, bus);
        zeroFlag_ = (regs_[r] == 0);
        ++pc_;
        break;
    case Opcode::JMP:
        pc_ = addr;
        break;
    case Opcode::JZ:
        pc_ = zeroFlag_ ? addr : pc_ + 1;
        break;
    case Opcode::HALT:
        halted_ = true;
        break;
    case Opcode::NOP:
    default:
        ++pc_;
        break;
    }

    return !halted_;
}

uint32_t CPU::GetPC() const { return pc_; }

uint32_t CPU::GetRegister(size_t index) const {
    if (index < regs_.size()) {
        return regs_[index];
    }
    return 0;
}

bool CPU::IsZeroFlagSet() const { return zeroFlag_; }

bool CPU::IsHalted() const { return halted_; }

std::string CPU::LastInstructionText() const { return lastInstructionText_; }
