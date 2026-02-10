package timer

// Timer belirli aralıkla interrupt üretir.
type Timer struct {
	name      string
	period    uint64
	counter   uint64
	irqRaised bool
}

func New(name string, period uint64) *Timer {
	if period == 0 {
		period = 100
	}
	return &Timer{name: name, period: period}
}

func (t *Timer) Name() string { return t.name }
func (t *Timer) Reset() {
	t.counter = 0
	t.irqRaised = false
}

func (t *Timer) Tick(_ uint64) {
	t.counter++
	if t.counter%t.period == 0 {
		t.irqRaised = true
	}
}

func (t *Timer) ConsumeIRQ() bool {
	if t.irqRaised {
		t.irqRaised = false
		return true
	}
	return false
}
