package bus

import (
	"fmt"

	"proje/peripheral"
	"proje/ram"
)

// Width veri yolunun bit genişliğini belirtir.
type Width int

const (
	Width16 Width = 16
	Width32 Width = 32
)

// Bus CPU ile RAM/IO arası haberleşmeyi yapar.
type Bus struct {
	width      Width
	ram        *ram.RAM
	ioDevices  []peripheral.MemoryMappedDevice
	ioBaseAddr uint32
}

func New(width Width, m *ram.RAM) (*Bus, error) {
	if width != Width16 && width != Width32 {
		return nil, fmt.Errorf("unsupported bus width: %d", width)
	}
	return &Bus{width: width, ram: m, ioBaseAddr: 0xF0000}, nil
}

func (b *Bus) Width() Width { return b.width }

func (b *Bus) AttachMemoryMappedDevice(d peripheral.MemoryMappedDevice) {
	b.ioDevices = append(b.ioDevices, d)
}

func (b *Bus) Read(addr uint32) (uint32, error) {
	for _, d := range b.ioDevices {
		if v, ok := d.Read(addr); ok {
			return v, nil
		}
	}
	if b.width == Width16 {
		lo, err := b.ram.Read8(addr)
		if err != nil {
			return 0, err
		}
		hi, err := b.ram.Read8(addr + 1)
		if err != nil {
			return 0, err
		}
		return uint32(lo) | uint32(hi)<<8, nil
	}
	return b.ram.Read32(addr)
}

func (b *Bus) Write(addr uint32, value uint32) error {
	for _, d := range b.ioDevices {
		if ok := d.Write(addr, value); ok {
			return nil
		}
	}
	if b.width == Width16 {
		if err := b.ram.Write8(addr, byte(value&0xFF)); err != nil {
			return err
		}
		return b.ram.Write8(addr+1, byte((value>>8)&0xFF))
	}
	return b.ram.Write32(addr, value)
}
