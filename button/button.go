package button

// Button basılma durumunu memory map üzerinden okunan birim olarak sunar.
type Button struct {
	name    string
	addr    uint32
	pressed bool
}

func New(name string, addr uint32) *Button { return &Button{name: name, addr: addr} }
func (b *Button) Name() string             { return b.name }
func (b *Button) Reset()                   { b.pressed = false }
func (b *Button) Tick(_ uint64)            {}

func (b *Button) SetPressed(v bool) { b.pressed = v }

func (b *Button) Read(addr uint32) (uint32, bool) {
	if addr != b.addr {
		return 0, false
	}
	if b.pressed {
		return 1, true
	}
	return 0, true
}

func (b *Button) Write(addr uint32, value uint32) bool {
	if addr != b.addr {
		return false
	}
	b.pressed = value&1 == 1
	return true
}
