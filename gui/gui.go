package gui

import (
	"fmt"
	"proje/emulator"
)

// GUI eğitim sürümü için soyut bir katmandır.
// Burada Fyne/Gio/Ebiten'e bağlanacak fonksiyonlar için sade bir iskelet bırakıldı.
type GUI struct {
	emu *emulator.Emulator
}

func New(emu *emulator.Emulator) *GUI {
	return &GUI{emu: emu}
}

// DrawFrame blok diyagram/panel çizimi için yer tutucu fonksiyondur.
func (g *GUI) DrawFrame() {
	fmt.Printf("[GUI] Cycle=%d Core0_PC=0x%X\n", g.emu.Cycle, g.emu.Cores[0].PC)
}
