package cpu

import "fmt"

// Opcode temel instruction set'i temsil eder.
type Opcode byte

const (
	NOP Opcode = iota
	LOAD
	STORE
	ADD
	SUB
	JMP
	JZ
	HALT
)

// Core tek bir CPU çekirdeğinin register/PC durumunu tutar.
type Core struct {
	ID        int
	Registers [8]uint32
	PC        uint32
	Halted    bool
}

func NewCore(id int) Core {
	return Core{ID: id}
}

// DecodedInstruction instruction alanlarını okunur biçimde sunar.
type DecodedInstruction struct {
	Op   Opcode
	A    byte
	B    byte
	C    byte
	Raw  uint32
	Addr uint32
}

func Decode(raw uint32) DecodedInstruction {
	a := byte((raw >> 16) & 0xFF)
	b := byte((raw >> 8) & 0xFF)
	c := byte(raw & 0xFF)
	return DecodedInstruction{
		Op:   Opcode((raw >> 24) & 0xFF),
		A:    a,
		B:    b,
		C:    c,
		Raw:  raw,
		Addr: uint32(b)<<8 | uint32(c),
	}
}

func (d DecodedInstruction) String() string {
	return fmt.Sprintf("op=%d a=%d b=%d c=%d addr=0x%X", d.Op, d.A, d.B, d.C, d.Addr)
}
