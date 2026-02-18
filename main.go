package main

import (
	"fmt"
	"math/rand"
	"os/exec"
	"runtime"
	"sort"
	"strings"
	"time"
	"unicode"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"
)

// Rotor represents a single Enigma rotor.
// Wiring maps input contact -> output contact in forward direction.
// Position is the rotational offset (0-25) and Notch triggers the rotor at left.
type Rotor struct {
	Wiring   [26]int
	Reverse  [26]int
	Position int
	Notch    int
	Name     string
}

func NewRotor(name, wiringStr string, notchRune rune, position int) (*Rotor, error) {
	if len(wiringStr) != 26 {
		return nil, fmt.Errorf("rotor wiring must have 26 chars")
	}
	r := &Rotor{Name: name}
	seen := map[int]bool{}
	for i, ch := range wiringStr {
		idx := int(ch - 'A')
		if idx < 0 || idx > 25 {
			return nil, fmt.Errorf("rotor wiring must contain only A-Z")
		}
		if seen[idx] {
			return nil, fmt.Errorf("rotor wiring must be permutation")
		}
		seen[idx] = true
		r.Wiring[i] = idx
	}
	for i := 0; i < 26; i++ {
		r.Reverse[r.Wiring[i]] = i
	}
	notch := int(unicode.ToUpper(notchRune) - 'A')
	if notch < 0 || notch > 25 {
		return nil, fmt.Errorf("invalid notch")
	}
	r.Notch = notch
	r.Position = ((position % 26) + 26) % 26
	return r, nil
}

func (r *Rotor) Step() {
	r.Position = (r.Position + 1) % 26
}

func (r *Rotor) AtNotch() bool {
	return r.Position == r.Notch
}

// Forward passes signal right->left through this rotor.
func (r *Rotor) Forward(c int) int {
	shifted := (c + r.Position) % 26
	wired := r.Wiring[shifted]
	return (wired - r.Position + 26) % 26
}

// Backward passes returning signal left->right through rotor reverse path.
func (r *Rotor) Backward(c int) int {
	shifted := (c + r.Position) % 26
	wired := r.Reverse[shifted]
	return (wired - r.Position + 26) % 26
}

// Reflector maps each letter to another and returns signal back.
type Reflector struct {
	Map [26]int
}

func NewReflector(mapping string) (*Reflector, error) {
	if len(mapping) != 26 {
		return nil, fmt.Errorf("reflector mapping must have 26 chars")
	}
	ref := &Reflector{}
	for i, ch := range mapping {
		idx := int(ch - 'A')
		if idx < 0 || idx > 25 {
			return nil, fmt.Errorf("reflector must contain only A-Z")
		}
		ref.Map[i] = idx
	}
	for i := 0; i < 26; i++ {
		if ref.Map[ref.Map[i]] != i || ref.Map[i] == i {
			return nil, fmt.Errorf("reflector must be symmetric and no self-map")
		}
	}
	return ref, nil
}

func (r *Reflector) Reflect(c int) int {
	return r.Map[c]
}

// Plugboard swaps letter pairs before and after rotor stack.
type Plugboard struct {
	Map [26]int
}

func NewPlugboard(spec string) (*Plugboard, error) {
	pb := &Plugboard{}
	for i := 0; i < 26; i++ {
		pb.Map[i] = i
	}
	spec = strings.TrimSpace(strings.ToUpper(spec))
	if spec == "" {
		return pb, nil
	}
	pairs := strings.Fields(spec)
	used := map[int]bool{}
	for _, p := range pairs {
		if len(p) != 2 {
			return nil, fmt.Errorf("invalid pair '%s'", p)
		}
		a := int(p[0] - 'A')
		b := int(p[1] - 'A')
		if a < 0 || a > 25 || b < 0 || b > 25 || a == b {
			return nil, fmt.Errorf("invalid pair '%s'", p)
		}
		if used[a] || used[b] {
			return nil, fmt.Errorf("plugboard letter reused in '%s'", p)
		}
		used[a], used[b] = true, true
		pb.Map[a], pb.Map[b] = b, a
	}
	return pb, nil
}

func (p *Plugboard) Swap(c int) int {
	return p.Map[c]
}

// EnigmaMachine keeps rotors from left->right as in historical notation.
type EnigmaMachine struct {
	Left      *Rotor
	Middle    *Rotor
	Right     *Rotor
	Reflector *Reflector
	Plugboard *Plugboard
}

func NewDefaultMachine(pos [3]int, plugSpec string) (*EnigmaMachine, error) {
	left, err := NewRotor("I", "EKMFLGDQVZNTOWYHXUSPAIBRCJ", 'Q', pos[0])
	if err != nil {
		return nil, err
	}
	middle, err := NewRotor("II", "AJDKSIRUXBLHWTMCQGZNPYFVOE", 'E', pos[1])
	if err != nil {
		return nil, err
	}
	right, err := NewRotor("III", "BDFHJLCPRTXVZNYEIWGAKMUSQO", 'V', pos[2])
	if err != nil {
		return nil, err
	}
	ref, err := NewReflector("YRUHQSLDPXNGOKMIEBFZCWVJAT") // Reflector B
	if err != nil {
		return nil, err
	}
	pb, err := NewPlugboard(plugSpec)
	if err != nil {
		return nil, err
	}
	return &EnigmaMachine{Left: left, Middle: middle, Right: right, Reflector: ref, Plugboard: pb}, nil
}

// stepRotors applies Enigma stepping with double-step behavior:
// - Right rotor always steps.
// - Middle rotor steps when right is at notch OR middle is at notch.
// - Left rotor steps when middle is at notch.
func (e *EnigmaMachine) stepRotors() {
	middleAtNotch := e.Middle.AtNotch()
	rightAtNotch := e.Right.AtNotch()

	if middleAtNotch {
		e.Left.Step()
	}
	if rightAtNotch || middleAtNotch {
		e.Middle.Step()
	}
	e.Right.Step()
}

// ProcessRune encrypts/decrypts one uppercase letter.
// Enigma is symmetric, so same flow handles both operations.
func (e *EnigmaMachine) ProcessRune(r rune) rune {
	if r < 'A' || r > 'Z' {
		return r
	}

	// 1) Step rotors before each keypress.
	e.stepRotors()

	c := int(r - 'A')
	// 2) Plugboard in.
	c = e.Plugboard.Swap(c)
	// 3) Through rotors right -> middle -> left.
	c = e.Right.Forward(c)
	c = e.Middle.Forward(c)
	c = e.Left.Forward(c)
	// 4) Reflect.
	c = e.Reflector.Reflect(c)
	// 5) Back through rotors left -> middle -> right.
	c = e.Left.Backward(c)
	c = e.Middle.Backward(c)
	c = e.Right.Backward(c)
	// 6) Plugboard out.
	c = e.Plugboard.Swap(c)

	return rune(c + 'A')
}

// ProcessMessage converts input to uppercase and processes only A-Z.
// keepSpaces keeps spaces/newlines/tabs; other chars are ignored.
func (e *EnigmaMachine) ProcessMessage(input string, keepSpaces bool) string {
	var b strings.Builder
	upper := strings.ToUpper(input)
	for _, r := range upper {
		if r >= 'A' && r <= 'Z' {
			b.WriteRune(e.ProcessRune(r))
			continue
		}
		if keepSpaces && (r == ' ' || r == '\n' || r == '\t') {
			b.WriteRune(r)
		}
	}
	return b.String()
}

// ProcessMessageWithTrace processes each key and returns trace lines with rotor positions.
func (e *EnigmaMachine) ProcessMessageWithTrace(input string, keepSpaces bool) (string, []string) {
	var out strings.Builder
	trace := make([]string, 0, len(input))
	for _, r := range strings.ToUpper(input) {
		if r >= 'A' && r <= 'Z' {
			before := fmt.Sprintf("%02d-%02d-%02d", e.Left.Position, e.Middle.Position, e.Right.Position)
			enc := e.ProcessRune(r)
			after := fmt.Sprintf("%02d-%02d-%02d", e.Left.Position, e.Middle.Position, e.Right.Position)
			out.WriteRune(enc)
			trace = append(trace, fmt.Sprintf("%c -> %c | rotor %s -> %s", r, enc, before, after))
			continue
		}
		if keepSpaces && (r == ' ' || r == '\n' || r == '\t') {
			out.WriteRune(r)
		}
	}
	return out.String(), trace
}

func parseRotorPos(text string) (int, error) {
	text = strings.TrimSpace(text)
	if text == "" {
		return 0, fmt.Errorf("boş olamaz")
	}
	v := 0
	for _, r := range text {
		if r < '0' || r > '9' {
			return 0, fmt.Errorf("0-25 arası sayı girin")
		}
		v = v*10 + int(r-'0')
	}
	if v > 25 {
		return 0, fmt.Errorf("0-25 arası olmalı")
	}
	return v, nil
}

func normalizePlugboardInput(s string) string {
	parts := strings.Fields(strings.ToUpper(strings.TrimSpace(s)))
	sort.Strings(parts)
	return strings.Join(parts, " ")
}

func randomPlugboardPairs(pairCount int) string {
	letters := []rune("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
	rand.Shuffle(len(letters), func(i, j int) {
		letters[i], letters[j] = letters[j], letters[i]
	})
	pairs := make([]string, 0, pairCount)
	for i := 0; i < pairCount*2; i += 2 {
		pairs = append(pairs, string([]rune{letters[i], letters[i+1]}))
	}
	sort.Strings(pairs)
	return strings.Join(pairs, " ")
}

func buildWindowsExe(statusLabel *widget.Label) {
	cmd := exec.Command("go", "build", "-o", "enigma-gui.exe", "main.go")
	cmd.Env = append(cmd.Env, "GOOS=windows", "GOARCH=amd64", "CGO_ENABLED=0")
	out, err := cmd.CombinedOutput()
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("EXE üretilemedi: %v | %s", err, strings.TrimSpace(string(out))))
		return
	}
	statusLabel.SetText("EXE hazır: enigma-gui.exe")
}

func buildNativeBinary(statusLabel *widget.Label) {
	name := "enigma-gui"
	if runtime.GOOS == "windows" {
		name += ".exe"
	}
	cmd := exec.Command("go", "build", "-o", name, "main.go")
	out, err := cmd.CombinedOutput()
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Yerel build hatası: %v | %s", err, strings.TrimSpace(string(out))))
		return
	}
	statusLabel.SetText("Yerel binary hazır: " + name)
}

func buildUI() fyne.Window {
	rand.Seed(time.Now().UnixNano())
	a := app.New()
	w := a.NewWindow("Enigma Benzeri Şifreleme")
	w.Resize(fyne.NewSize(980, 760))

	inputEntry := widget.NewMultiLineEntry()
	inputEntry.SetPlaceHolder("Mesajı buraya yazın...")
	outputEntry := widget.NewMultiLineEntry()
	outputEntry.SetPlaceHolder("Çıktı burada görünecek...")
	traceEntry := widget.NewMultiLineEntry()
	traceEntry.SetPlaceHolder("Her harf için rotor adımı burada görünecek...")
	traceEntry.Disable()

	rotorLeft := widget.NewEntry()
	rotorLeft.SetText("0")
	rotorMid := widget.NewEntry()
	rotorMid.SetText("0")
	rotorRight := widget.NewEntry()
	rotorRight.SetText("0")

	plugEntry := widget.NewEntry()
	plugEntry.SetPlaceHolder("Örn: AB CD EF")

	keepSpacesCheck := widget.NewCheck("Boşlukları koru", nil)
	keepSpacesCheck.SetChecked(true)

	traceCheck := widget.NewCheck("Tuş başına rotor izleme göster", nil)
	traceCheck.SetChecked(true)

	rotorStateLabel := widget.NewLabel("Rotorlar (L-M-R): 0-0-0")
	statusLabel := widget.NewLabel("Hazır")

	process := func(action string) {
		l, err := parseRotorPos(rotorLeft.Text)
		if err != nil {
			statusLabel.SetText("Sol rotor hatası: " + err.Error())
			return
		}
		m, err := parseRotorPos(rotorMid.Text)
		if err != nil {
			statusLabel.SetText("Orta rotor hatası: " + err.Error())
			return
		}
		r, err := parseRotorPos(rotorRight.Text)
		if err != nil {
			statusLabel.SetText("Sağ rotor hatası: " + err.Error())
			return
		}

		machine, err := NewDefaultMachine([3]int{l, m, r}, normalizePlugboardInput(plugEntry.Text))
		if err != nil {
			statusLabel.SetText("Ayar hatası: " + err.Error())
			return
		}

		result, trace := machine.ProcessMessageWithTrace(inputEntry.Text, keepSpacesCheck.Checked)
		outputEntry.SetText(result)
		rotorStateLabel.SetText(fmt.Sprintf("Rotorlar (L-M-R): %d-%d-%d", machine.Left.Position, machine.Middle.Position, machine.Right.Position))

		if traceCheck.Checked {
			traceEntry.SetText(strings.Join(trace, "\n"))
		} else {
			traceEntry.SetText("")
		}
		statusLabel.SetText(action + " tamamlandı (Enigma simetrik: aynı ayar ile geri çözülür)")
	}

	encryptBtn := widget.NewButton("Şifrele", func() { process("Şifreleme") })
	decryptBtn := widget.NewButton("Çöz", func() { process("Çözme") })
	resetBtn := widget.NewButton("Sıfırla", func() {
		inputEntry.SetText("")
		outputEntry.SetText("")
		traceEntry.SetText("")
		rotorLeft.SetText("0")
		rotorMid.SetText("0")
		rotorRight.SetText("0")
		plugEntry.SetText("")
		keepSpacesCheck.SetChecked(true)
		traceCheck.SetChecked(true)
		rotorStateLabel.SetText("Rotorlar (L-M-R): 0-0-0")
		statusLabel.SetText("Sıfırlandı")
	})

	randomSettingsBtn := widget.NewButton("Rastgele Ayar", func() {
		rotorLeft.SetText(fmt.Sprintf("%d", rand.Intn(26)))
		rotorMid.SetText(fmt.Sprintf("%d", rand.Intn(26)))
		rotorRight.SetText(fmt.Sprintf("%d", rand.Intn(26)))
		plugEntry.SetText(randomPlugboardPairs(5))
		statusLabel.SetText("Rastgele rotor ve plugboard ayarları üretildi")
	})

	swapBtn := widget.NewButton("Girdi/Çıktı Değiştir", func() {
		oldIn := inputEntry.Text
		inputEntry.SetText(outputEntry.Text)
		outputEntry.SetText(oldIn)
		statusLabel.SetText("Girdi ve çıktı alanları yer değiştirildi")
	})

	exeBtn := widget.NewButton("Windows EXE Üret", func() {
		buildWindowsExe(statusLabel)
	})

	nativeBuildBtn := widget.NewButton("Yerel Binary Üret", func() {
		buildNativeBinary(statusLabel)
	})

	copyBtn := widget.NewButton("Çıktıyı Girdiye Kopyala", func() {
		inputEntry.SetText(outputEntry.Text)
		statusLabel.SetText("Çıktı metni girdi alanına kopyalandı")
	})

	aboutBtn := widget.NewButton("Hakkında", func() {
		dialog.ShowInformation(
			"Enigma GUI",
			"3 rotor + reflektör + plugboard\nDouble-step rotor mekanizması\nEkstra: tuş izi, rastgele ayar, binary üretimi",
			w,
		)
	})

	form := &widget.Form{Items: []*widget.FormItem{
		{Text: "Rotor Sol (0-25)", Widget: rotorLeft},
		{Text: "Rotor Orta (0-25)", Widget: rotorMid},
		{Text: "Rotor Sağ (0-25)", Widget: rotorRight},
		{Text: "Plugboard", Widget: plugEntry},
	}}

	content := container.NewVBox(
		widget.NewLabelWithStyle("Enigma Benzeri Mesaj Şifreleme / Çözme", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}),
		widget.NewLabel("Yalnızca A-Z işlenir. Şifrele ve Çöz aynı ayarlarla simetrik çalışır."),
		form,
		container.NewGridWithColumns(2, keepSpacesCheck, traceCheck),
		widget.NewLabel("Giriş Mesajı"),
		inputEntry,
		container.NewGridWithColumns(4, encryptBtn, decryptBtn, swapBtn, resetBtn),
		container.NewGridWithColumns(4, randomSettingsBtn, copyBtn, nativeBuildBtn, exeBtn),
		aboutBtn,
		widget.NewLabel("Çıktı"),
		outputEntry,
		widget.NewLabel("Tuş İzleme"),
		traceEntry,
		rotorStateLabel,
		statusLabel,
	)

	w.SetContent(content)
	return w
}

func main() {
	w := buildUI()
	w.ShowAndRun()
}
