package main

import (
	"bufio"
	"fmt"
	"os"
	"runtime"
	"strings"

	"proje/adc"
	"proje/bus"
	"proje/button"
	"proje/dac"
	"proje/emulator"
	"proje/gui"
	"proje/led"
	"proje/loader"
	"proje/screen"
)

func main() {
	exitCode := run()
	waitOnExitIfNeeded()
	os.Exit(exitCode)
}

func run() int {
	emu, err := emulator.New(2, bus.Width32)
	if err != nil {
		fmt.Println("[ERROR] Emulator init failed:", err)
		return 1
	}

	// Basit bellek map'i
	led0 := led.New("LED0", 0x0100)
	btn0 := button.New("BTN0", 0x0104)
	scr0 := screen.New("SCR0", 0x0108)
	adc0 := adc.New("ADC0", 0x0110, 1023)
	dac0 := dac.New("DAC0", 0x0114, 1023)

	emu.AttachDevice(led0)
	emu.AttachDevice(btn0)
	emu.AttachDevice(scr0)
	emu.AttachDevice(adc0)
	emu.AttachDevice(dac0)

	// Program dosyası verilmişse loader kullanılır, yoksa demo program.
	var code []byte
	if len(os.Args) > 1 {
		p, err := loader.Load(os.Args[1])
		if err != nil {
			fmt.Println("[ERROR] Program load failed:", err)
			return 1
		}
		code = p.Bytes
	} else {
		// Demo: R0 = ADC oku, LED'e yaz, ekrana 'A' yaz, HALT
		code = []byte{
			0x10, 0x01, 0x00, 0x01, // LOAD R0, [0x0110]
			0x00, 0x01, 0x00, 0x02, // STORE R0, [0x0100]
			'A', 0x00, 0x00, 0x01, // LOAD R0, [0x0041] (örnek amaçlı)
			0x08, 0x01, 0x00, 0x02, // STORE R0, [0x0108]
			0x00, 0x00, 0x00, 0x07, // HALT
		}
		if err := emu.RAM.Write32(0x0041, 'A'); err != nil {
			fmt.Println("[ERROR] Demo RAM write failed:", err)
			return 1
		}
	}

	if err := emu.LoadProgram(code, 0); err != nil {
		fmt.Println("[ERROR] Program map failed:", err)
		return 1
	}
	adc0.SetAnalogInput(0.75)

	emu.AddBreakpoint(0xFFFFFFFE) // örnek amaçlı, tetiklenmez
	emu.AddWatchpoint(0x0100)

	if err := emu.Run(16); err != nil {
		fmt.Println("[WARN] Run stopped:", err)
	}

	ui := gui.New(emu)
	ui.DrawFrame()

	fmt.Println(led0.String())
	fmt.Println("Screen:", scr0.Render())
	fmt.Printf("DAC out: %.2f\n", dac0.AnalogOut())
	fmt.Printf("Core0 regs: %+v\n", emu.Cores[0].Registers)
	return 0
}

func waitOnExitIfNeeded() {
	if runtime.GOOS != "windows" {
		return
	}
	v := strings.TrimSpace(strings.ToLower(os.Getenv("MCU_WAIT_ON_EXIT")))
	if v != "1" && v != "true" && v != "yes" {
		return
	}
	fmt.Print("\n[INFO] Cikmak icin Enter tusuna basin...")
	_, _ = bufio.NewReader(os.Stdin).ReadString('\n')
}
