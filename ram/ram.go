package ram

import (
	"errors"
	"fmt"
	"sync"
)

const (
	// MaxSize toplam RAM kapasitesi: 1 MB.
	MaxSize = 1024 * 1024
)

// SegmentStartEnd bellek segmentlerinin sınırlarını tutar.
type SegmentStartEnd struct {
	Start uint32
	End   uint32
}

// Layout segmentli bellek düzenini temsil eder.
type Layout struct {
	Data  SegmentStartEnd
	BSS   SegmentStartEnd
	Heap  SegmentStartEnd
	Stack SegmentStartEnd
}

// RAM thread-safe bir byte dizisi ve segment tanımından oluşur.
type RAM struct {
	mu     sync.RWMutex
	memory []byte
	layout Layout
}

func New() *RAM {
	mem := make([]byte, MaxSize)
	return &RAM{
		memory: mem,
		layout: Layout{
			Data:  SegmentStartEnd{Start: 0x00000, End: 0x1FFFF},
			BSS:   SegmentStartEnd{Start: 0x20000, End: 0x2FFFF},
			Heap:  SegmentStartEnd{Start: 0x30000, End: 0x7FFFF},
			Stack: SegmentStartEnd{Start: 0x80000, End: 0xFFFFF},
		},
	}
}

func (r *RAM) Layout() Layout {
	return r.layout
}

func (r *RAM) check(addr uint32, size uint32) error {
	if addr+size > uint32(len(r.memory)) {
		return fmt.Errorf("ram out of range addr=0x%X size=%d", addr, size)
	}
	return nil
}

func (r *RAM) Read8(addr uint32) (byte, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	if err := r.check(addr, 1); err != nil {
		return 0, err
	}
	return r.memory[addr], nil
}

func (r *RAM) Write8(addr uint32, v byte) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if err := r.check(addr, 1); err != nil {
		return err
	}
	r.memory[addr] = v
	return nil
}

func (r *RAM) Read32(addr uint32) (uint32, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	if err := r.check(addr, 4); err != nil {
		return 0, err
	}
	v := uint32(r.memory[addr]) |
		uint32(r.memory[addr+1])<<8 |
		uint32(r.memory[addr+2])<<16 |
		uint32(r.memory[addr+3])<<24
	return v, nil
}

func (r *RAM) Write32(addr uint32, v uint32) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if err := r.check(addr, 4); err != nil {
		return err
	}
	r.memory[addr] = byte(v & 0xFF)
	r.memory[addr+1] = byte((v >> 8) & 0xFF)
	r.memory[addr+2] = byte((v >> 16) & 0xFF)
	r.memory[addr+3] = byte((v >> 24) & 0xFF)
	return nil
}

func (r *RAM) LoadBytes(start uint32, data []byte) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if err := r.check(start, uint32(len(data))); err != nil {
		return err
	}
	copy(r.memory[start:], data)
	return nil
}

func (r *RAM) Dump(start, end uint32) ([]byte, error) {
	if end < start {
		return nil, errors.New("invalid range: end < start")
	}
	r.mu.RLock()
	defer r.mu.RUnlock()
	if err := r.check(start, end-start+1); err != nil {
		return nil, err
	}
	out := make([]byte, end-start+1)
	copy(out, r.memory[start:end+1])
	return out, nil
}

func (r *RAM) Reset() {
	r.mu.Lock()
	defer r.mu.Unlock()
	for i := range r.memory {
		r.memory[i] = 0
	}
}
