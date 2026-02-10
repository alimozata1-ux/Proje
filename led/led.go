package led

import "fmt"

// LED bellek map üzerinden aç/kapa kontrol edilen basit bir çevresel birimdir.
type LED struct {
	name  string
	addr  uint32
	state bool
}

func New(name string, addr uint32) *LED { return &LED{name: name, addr: addr} }
func (l *LED) Name() string             { return l.name }
func (l *LED) Reset()                   { l.state = false }
func (l *LED) Tick(_ uint64)            {}
func (l *LED) State() bool              { return l.state }

func (l *LED) Read(addr uint32) (uint32, bool) {
	if addr != l.addr {
		return 0, false
	}
	if l.state {
		return 1, true
	}
	return 0, true
}

func (l *LED) Write(addr uint32, value uint32) bool {
	if addr != l.addr {
		return false
	}
	l.state = value&1 == 1
	return true
}

func (l *LED) String() string {
	if l.state {
		return fmt.Sprintf("%s: ON", l.name)
	}
	return fmt.Sprintf("%s: OFF", l.name)
}
