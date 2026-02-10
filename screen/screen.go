package screen

import "fmt"

// Screen eğitim amaçlı tek register'lık 7-segment benzeri bir simülasyondur.
type Screen struct {
	name string
	addr uint32
	char byte
}

func New(name string, addr uint32) *Screen { return &Screen{name: name, addr: addr, char: ' '} }
func (s *Screen) Name() string             { return s.name }
func (s *Screen) Reset()                   { s.char = ' ' }
func (s *Screen) Tick(_ uint64)            {}

func (s *Screen) Read(addr uint32) (uint32, bool) {
	if addr != s.addr {
		return 0, false
	}
	return uint32(s.char), true
}

func (s *Screen) Write(addr uint32, value uint32) bool {
	if addr != s.addr {
		return false
	}
	s.char = byte(value & 0x7F)
	return true
}

func (s *Screen) Render() string {
	return fmt.Sprintf("[%c]", s.char)
}
