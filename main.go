// Windows için basit GUI sistem izleyici (System Monitor)
//
// Kurulum adımları:
// 1) Go kur:
//    - Windows'ta resmi yükleyici: https://go.dev/dl/
//    - Kurulumdan sonra doğrula: go version
//
// 2) Projeyi hazırla ve bağımlılıkları ekle:
//    - go mod init system-monitor
//    - go get github.com/shirou/gopsutil/v3
//    - go get github.com/lxn/walk
//
// 3) Çalıştır:
//    - go run .
//
// 4) Windows .exe oluştur:
//    - Otomatik script ile (önerilen): build.bat
//    - Manuel: GOOS=windows GOARCH=amd64 go build -ldflags="-H windowsgui" -o system-monitor.exe

package main

import (
	"fmt"
	"runtime"
	"time"

	"github.com/lxn/walk"
	. "github.com/lxn/walk/declarative"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/mem"
)

func main() {
	var mainWindow *walk.MainWindow
	var cpuLabel *walk.Label
	var ramLabel *walk.Label
	var diskLabel *walk.Label

	// Disk kullanım yolu işletim sistemine göre seçilir.
	diskPath := "/"
	if runtime.GOOS == "windows" {
		diskPath = "C:\\"
	}

	// Basit ve okunabilir GUI penceresi oluşturulur.
	window := MainWindow{
		AssignTo: &mainWindow,
		Title:    "System Monitor",
		MinSize:  Size{Width: 300, Height: 180},
		Layout:   VBox{},
		Children: []Widget{
			Label{AssignTo: &cpuLabel, Text: "🖥️ CPU: -"},
			Label{AssignTo: &ramLabel, Text: "🧠 RAM: -"},
			Label{AssignTo: &diskLabel, Text: "💾 Disk: -"},
		},
	}

	if err := window.Create(); err != nil {
		fmt.Printf("Pencere oluşturulamadı: %v\n", err)
		return
	}

	// Her saniye ölçüm yapan goroutine.
	go func() {
		ticker := time.NewTicker(1 * time.Second)
		defer ticker.Stop()

		for range ticker.C {
			cpuText := "🖥️ CPU: -"
			ramText := "🧠 RAM: -"
			diskText := "💾 Disk: -"

			// CPU ölçümü: hata durumunda uygulama kapanmaz.
			cpuPercents, cpuErr := cpu.Percent(0, false)
			if cpuErr != nil || len(cpuPercents) == 0 {
				cpuText = fmt.Sprintf("🖥️ CPU: hata (%v)", cpuErr)
			} else {
				cpuText = fmt.Sprintf("🖥️ CPU: %.1f%%", cpuPercents[0])
			}

			// RAM ölçümü: hata durumunda uygulama kapanmaz.
			vm, memErr := mem.VirtualMemory()
			if memErr != nil {
				ramText = fmt.Sprintf("🧠 RAM: hata (%v)", memErr)
			} else {
				ramText = fmt.Sprintf("🧠 RAM: %.1f%%", vm.UsedPercent)
			}

			// Disk ölçümü: hata durumunda uygulama kapanmaz.
			diskUsage, diskErr := disk.Usage(diskPath)
			if diskErr != nil {
				diskText = fmt.Sprintf("💾 Disk: hata (%v)", diskErr)
			} else {
				diskText = fmt.Sprintf("💾 Disk: %.1f%%", diskUsage.UsedPercent)
			}

			// GUI elemanları yalnızca UI thread üzerinde güncellenir.
			mainWindow.Synchronize(func() {
				cpuLabel.SetText(cpuText)
				ramLabel.SetText(ramText)
				diskLabel.SetText(diskText)
			})
		}
	}()

	mainWindow.Run()
}
