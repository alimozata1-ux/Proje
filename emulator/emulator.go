package emulator

import (
	"errors"
	"fmt"
	"sync"

	"proje/bus"
	"proje/cpu"
	"proje/peripheral"
	"proje/ram"
	"proje/timer"
)

// Emulator CPU çekirdekleri ve çevreselleri birlikte çalıştırır.
type Emulator struct {
	mu sync.Mutex

	RAM   *ram.RAM
	Bus   *bus.Bus
	Cores []cpu.Core

	Devices []peripheral.Device
	Timer   *timer.Timer

	Running bool
	Cycle   uint64

	breakpoints map[uint32]struct{}
	watchpoints map[uint32]struct{}
}

func New(coreCount int, busWidth bus.Width) (*Emulator, error) {
	if coreCount != 2 && coreCount != 4 {
		return nil, fmt.Errorf("coreCount must be 2 or 4")
	}
	m := ram.New()
	b, err := bus.New(busWidth, m)
	if err != nil {
		return nil, err
	}
	cores := make([]cpu.Core, coreCount)
	for i := 0; i < coreCount; i++ {
		cores[i] = cpu.NewCore(i)
	}
	return &Emulator{
		RAM:         m,
		Bus:         b,
		Cores:       cores,
		Timer:       timer.New("sys_timer", 50),
		breakpoints: map[uint32]struct{}{},
		watchpoints: map[uint32]struct{}{},
	}, nil
}

func (e *Emulator) AttachDevice(d peripheral.Device) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.Devices = append(e.Devices, d)
	if mm, ok := d.(peripheral.MemoryMappedDevice); ok {
		e.Bus.AttachMemoryMappedDevice(mm)
	}
}

func (e *Emulator) LoadProgram(code []byte, start uint32) error {
	return e.RAM.LoadBytes(start, code)
}

func (e *Emulator) AddBreakpoint(addr uint32) { e.breakpoints[addr] = struct{}{} }
func (e *Emulator) AddWatchpoint(addr uint32) { e.watchpoints[addr] = struct{}{} }

func (e *Emulator) Reset() {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.Running = false
	e.Cycle = 0
	e.RAM.Reset()
	for i := range e.Cores {
		e.Cores[i] = cpu.NewCore(i)
	}
	for _, d := range e.Devices {
		d.Reset()
	}
	e.Timer.Reset()
}

func (e *Emulator) Step(coreID int) error {
	e.mu.Lock()
	defer e.mu.Unlock()
	if coreID < 0 || coreID >= len(e.Cores) {
		return errors.New("invalid core id")
	}
	c := &e.Cores[coreID]
	if c.Halted {
		return nil
	}
	if _, ok := e.breakpoints[c.PC]; ok {
		e.Running = false
		return fmt.Errorf("breakpoint hit at 0x%X", c.PC)
	}

	raw, err := e.Bus.Read(c.PC)
	if err != nil {
		return err
	}
	inst := cpu.Decode(raw)
	c.PC += 4

	switch inst.Op {
	case cpu.NOP:
	case cpu.LOAD:
		v, err := e.Bus.Read(inst.Addr)
		if err != nil {
			return err
		}
		c.Registers[inst.A%8] = v
	case cpu.STORE:
		addr := inst.Addr
		if _, watched := e.watchpoints[addr]; watched {
			fmt.Printf("watchpoint write at 0x%X\n", addr)
		}
		if err := e.Bus.Write(addr, c.Registers[inst.A%8]); err != nil {
			return err
		}
	case cpu.ADD:
		c.Registers[inst.A%8] += c.Registers[inst.B%8]
	case cpu.SUB:
		c.Registers[inst.A%8] -= c.Registers[inst.B%8]
	case cpu.JMP:
		c.PC = inst.Addr
	case cpu.JZ:
		if c.Registers[inst.A%8] == 0 {
			c.PC = inst.Addr
		}
	case cpu.HALT:
		c.Halted = true
	default:
		return fmt.Errorf("unknown opcode: %d", inst.Op)
	}

	e.Cycle++
	for _, d := range e.Devices {
		d.Tick(e.Cycle)
	}
	e.Timer.Tick(e.Cycle)
	if e.Timer.ConsumeIRQ() {
		// Eğitim amaçlı: IRQ gelince core0'ın R7 register'ına sayaç artırıyoruz.
		e.Cores[0].Registers[7]++
	}
	return nil
}

func (e *Emulator) Run(steps int) error {
	e.Running = true
	for i := 0; i < steps; i++ {
		for core := range e.Cores {
			if err := e.Step(core); err != nil {
				e.Running = false
				return err
			}
		}
	}
	e.Running = false
	return nil
}

func (e *Emulator) Pause() { e.Running = false }
