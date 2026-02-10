package adc

// ADC analog giriş değerini sayısal değere çevirir.
type ADC struct {
	name       string
	addr       uint32
	resolution uint32
	analogIn   float64 // 0..1
}

func New(name string, addr uint32, resolution uint32) *ADC {
	if resolution == 0 {
		resolution = 1023
	}
	return &ADC{name: name, addr: addr, resolution: resolution}
}

func (a *ADC) Name() string  { return a.name }
func (a *ADC) Reset()        { a.analogIn = 0 }
func (a *ADC) Tick(_ uint64) {}

func (a *ADC) SetAnalogInput(v float64) {
	if v < 0 {
		v = 0
	}
	if v > 1 {
		v = 1
	}
	a.analogIn = v
}

func (a *ADC) Read(addr uint32) (uint32, bool) {
	if addr != a.addr {
		return 0, false
	}
	return uint32(a.analogIn * float64(a.resolution)), true
}

func (a *ADC) Write(addr uint32, _ uint32) bool {
	return addr == a.addr // yazma yok; noop
}
