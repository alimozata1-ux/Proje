package dac

// DAC dijital değeri analog çıkışa dönüştürür (0..1 normalize).
type DAC struct {
	name       string
	addr       uint32
	resolution uint32
	lastValue  uint32
}

func New(name string, addr uint32, resolution uint32) *DAC {
	if resolution == 0 {
		resolution = 1023
	}
	return &DAC{name: name, addr: addr, resolution: resolution}
}

func (d *DAC) Name() string  { return d.name }
func (d *DAC) Reset()        { d.lastValue = 0 }
func (d *DAC) Tick(_ uint64) {}

func (d *DAC) AnalogOut() float64 {
	return float64(d.lastValue) / float64(d.resolution)
}

func (d *DAC) Read(addr uint32) (uint32, bool) {
	if addr != d.addr {
		return 0, false
	}
	return d.lastValue, true
}

func (d *DAC) Write(addr uint32, value uint32) bool {
	if addr != d.addr {
		return false
	}
	if value > d.resolution {
		value = d.resolution
	}
	d.lastValue = value
	return true
}
