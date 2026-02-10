package peripheral

// Device, emülatöre takılabilen tüm çevresel birimlerin uyguladığı temel arayüzdür.
// Tick() fonksiyonu emülatör döngüsünde düzenli çağrılarak zaman tabanlı davranışları sağlar.
type Device interface {
	Name() string
	Reset()
	Tick(cycle uint64)
}

// MemoryMappedDevice, bellek alanına map edilmiş çevresel birimler için opsiyonel arayüzdür.
type MemoryMappedDevice interface {
	Device
	Read(addr uint32) (uint32, bool)
	Write(addr uint32, value uint32) bool
}
