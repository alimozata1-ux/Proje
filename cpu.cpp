#include "cpu.h"
#include <sstream>

CPU::CPU() {
    reset();
}

void CPU::reset(uint32_t startAddress) {
    regs_.fill(0);
    pc_ = startAddress;
    zeroFlag_ = false;
    halted_ = false;
    lastInst_ = {};
}

uint16_t CPU::makeAddress(uint8_t hi, uint8_t lo) {
    return static_cast<uint16_t>((static_cast<uint16_t>(hi) << 8) | lo);
}

CPU::Instruction CPU::fetch(ROM& rom, Bus& bus) {
    Instruction inst{};
    uint8_t bytes[4] = {0, 0, 0, 0};

    for (uint32_t i = 0; i < 4; ++i) {
        uint8_t v = 0;
        rom.read(pc_ + i, v);
        bytes[i] = v;
    }

    bus.setAddress(pc_);
    bus.setData(bytes[0]);
    bus.setControl(0x1); // fetch

    inst.opcode = static_cast<Opcode>(bytes[0]);
    inst.a = bytes[1];
    inst.b = bytes[2];
    inst.c = bytes[3];
    return inst;
}

bool CPU::step(ROM& rom, RAM& ram, Bus& bus) {
    if (halted_) return false;

    Instruction inst = fetch(rom, bus);
    lastInst_ = inst;
    pc_ += 4;

    const auto regIdxA = static_cast<std::size_t>(inst.a % regs_.size());
    const auto regIdxB = static_cast<std::size_t>(inst.b % regs_.size());

    switch (inst.opcode) {
    case Opcode::NOP:
        break;
    case Opcode::LOAD: {
        uint8_t value = 0;
        uint16_t addr = makeAddress(inst.b, inst.c);
        if (ram.read(addr, value)) {
            regs_[regIdxA] = value;
            zeroFlag_ = (regs_[regIdxA] == 0);
            bus.setAddress(addr);
            bus.setData(value);
            bus.setControl(0x2); // read
        }
        break;
    }
    case Opcode::STORE: {
        uint16_t addr = makeAddress(inst.b, inst.c);
        uint8_t value = static_cast<uint8_t>(regs_[regIdxA] & 0xFFu);
        ram.write(addr, value);
        bus.setAddress(addr);
        bus.setData(value);
        bus.setControl(0x4); // write
        break;
    }
    case Opcode::ADD: {
        auto r = alu_.add(regs_[regIdxA], regs_[regIdxB]);
        regs_[regIdxA] = r.value;
        zeroFlag_ = r.zero;
        break;
    }
    case Opcode::SUB: {
        auto r = alu_.sub(regs_[regIdxA], regs_[regIdxB]);
        regs_[regIdxA] = r.value;
        zeroFlag_ = r.zero;
        break;
    }
    case Opcode::JMP:
        pc_ = makeAddress(inst.b, inst.c);
        break;
    case Opcode::JZ:
        if (zeroFlag_) pc_ = makeAddress(inst.b, inst.c);
        break;
    case Opcode::HALT:
        halted_ = true;
        break;
    default:
        halted_ = true;
        break;
    }

    return !halted_;
}

std::string CPU::lastInstructionText() const {
    std::ostringstream oss;
    auto op = lastInst_.opcode;

    switch (op) {
    case Opcode::NOP: oss << "NOP"; break;
    case Opcode::LOAD: oss << "LOAD R" << +lastInst_.a << ", [0x" << std::hex << +makeAddress(lastInst_.b, lastInst_.c) << "]"; break;
    case Opcode::STORE: oss << "STORE R" << +lastInst_.a << ", [0x" << std::hex << +makeAddress(lastInst_.b, lastInst_.c) << "]"; break;
    case Opcode::ADD: oss << "ADD R" << +lastInst_.a << ", R" << +lastInst_.b; break;
    case Opcode::SUB: oss << "SUB R" << +lastInst_.a << ", R" << +lastInst_.b; break;
    case Opcode::JMP: oss << "JMP 0x" << std::hex << +makeAddress(lastInst_.b, lastInst_.c); break;
    case Opcode::JZ: oss << "JZ 0x" << std::hex << +makeAddress(lastInst_.b, lastInst_.c); break;
    case Opcode::HALT: oss << "HALT"; break;
    default: oss << "UNKNOWN"; break;
    }
    return oss.str();
}
