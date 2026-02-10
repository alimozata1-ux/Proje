// Windows için basit sistem izleyici (System Monitor)
//
// Kurulum adımları:
// 1) Go kur:
//    - Windows'ta resmi yükleyici: https://go.dev/dl/
//    - Kurulumdan sonra doğrula: go version
//
// 2) Projeyi hazırla ve bağımlılığı ekle:
//    - go mod init system-monitor
//    - go get github.com/shirou/gopsutil/v3
//
// 3) Çalıştır:
//    - go run .
//
// 4) Windows .exe oluştur:
//    - go build -o system-monitor.exe
//    - (Başka işletim sisteminden Windows için derlemek istersen)
//      GOOS=windows GOARCH=amd64 go build -o system-monitor.exe

package main

import (
	"fmt"
	"runtime"
	"time"

	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/mem"
)

const (
	cpuIcon  = "🖥️"
	ramIcon  = "🧠"
	diskIcon = "💾"
)

func main() {
	// Disk kullanım yolunu işletim sistemine göre belirle.
	// Windows için C:\\, diğerleri için / kullanılır.
	diskPath := "/"
	if runtime.GOOS == "windows" {
		diskPath = "C:\\"
	}

	// Her saniye metrik toplamak için sonsuz döngü.
	for {
		// CPU kullanımı: interval=0 ile son ölçümden bu yana anlık değer alınır.
		cpuPercents, cpuErr := cpu.Percent(0, false)

		// RAM kullanımı bilgisi.
		vm, memErr := mem.VirtualMemory()

		// Disk kullanımı bilgisi (Windows'ta C:\\ sürücüsü).
		diskUsage, diskErr := disk.Usage(diskPath)

		// CPU çıktısı: hata varsa programı durdurmadan hata mesajı yaz.
		if cpuErr != nil || len(cpuPercents) == 0 {
			fmt.Printf("%s CPU: hata (%v)\n", cpuIcon, cpuErr)
		} else {
			fmt.Printf("%s CPU: %.1f%%\n", cpuIcon, cpuPercents[0])
		}

		// RAM çıktısı: hata varsa programı durdurmadan hata mesajı yaz.
		if memErr != nil {
			fmt.Printf("%s RAM: hata (%v)\n", ramIcon, memErr)
		} else {
			fmt.Printf("%s RAM: %.1f%%\n", ramIcon, vm.UsedPercent)
		}

		// Disk çıktısı: hata varsa programı durdurmadan hata mesajı yaz.
		if diskErr != nil {
			fmt.Printf("%s Disk: hata (%v)\n", diskIcon, diskErr)
		} else {
			fmt.Printf("%s Disk: %.1f%%\n", diskIcon, diskUsage.UsedPercent)
		}

		fmt.Println()

		// Bir sonraki ölçüm için 1 saniye bekle.
		time.Sleep(1 * time.Second)
	}
}
