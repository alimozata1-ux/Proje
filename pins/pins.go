package pins

import "sync"

// DigitalValue dijital pin seviyesini temsil eder.
type DigitalValue bool

const (
	Low  DigitalValue = false
	High DigitalValue = true
)

// PinBank analog+dijital pin durumlarını tutar.
type PinBank struct {
	mu      sync.RWMutex
	digital map[int]DigitalValue
	analog  map[int]float64 // 0.0 .. 1.0
}

func New() *PinBank {
	return &PinBank{
		digital: map[int]DigitalValue{},
		analog:  map[int]float64{},
	}
}

func (p *PinBank) SetDigital(idx int, v DigitalValue) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.digital[idx] = v
}

func (p *PinBank) Digital(idx int) DigitalValue {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.digital[idx]
}

func (p *PinBank) SetAnalog(idx int, v float64) {
	if v < 0 {
		v = 0
	}
	if v > 1 {
		v = 1
	}
	p.mu.Lock()
	defer p.mu.Unlock()
	p.analog[idx] = v
}

func (p *PinBank) Analog(idx int) float64 {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.analog[idx]
}
