package loader

import (
	"bufio"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// Program yüklenen byte kodu ve entry point adresini içerir.
type Program struct {
	Bytes      []byte
	EntryPoint uint32
}

func Load(path string) (Program, error) {
	ext := strings.ToLower(filepath.Ext(path))
	switch ext {
	case ".bin":
		return loadBIN(path)
	case ".hex":
		return loadHEX(path)
	case ".c":
		return loadPseudoC(path)
	default:
		return Program{}, fmt.Errorf("unsupported extension: %s", ext)
	}
}

func loadBIN(path string) (Program, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return Program{}, err
	}
	return Program{Bytes: b, EntryPoint: 0}, nil
}

func loadHEX(path string) (Program, error) {
	txt, err := os.ReadFile(path)
	if err != nil {
		return Program{}, err
	}
	raw := strings.ReplaceAll(string(txt), "\n", "")
	raw = strings.ReplaceAll(raw, " ", "")
	b, err := hex.DecodeString(raw)
	if err != nil {
		return Program{}, err
	}
	return Program{Bytes: b, EntryPoint: 0}, nil
}

// loadPseudoC eğitim amaçlı basit bir pseudo-compiler içerir.
// Desteklenen satır örneği: ADD 0 1
func loadPseudoC(path string) (Program, error) {
	f, err := os.Open(path)
	if err != nil {
		return Program{}, err
	}
	defer f.Close()

	var out []byte
	s := bufio.NewScanner(f)
	for s.Scan() {
		line := strings.TrimSpace(s.Text())
		if line == "" || strings.HasPrefix(line, "//") {
			continue
		}
		inst, err := compileLine(line)
		if err != nil {
			return Program{}, err
		}
		out = append(out, inst...)
	}
	if err := s.Err(); err != nil {
		return Program{}, err
	}
	return Program{Bytes: out, EntryPoint: 0}, nil
}

func compileLine(line string) ([]byte, error) {
	parts := strings.Fields(strings.ToUpper(line))
	if len(parts) == 0 {
		return nil, fmt.Errorf("empty line")
	}
	opcodeMap := map[string]byte{
		"NOP":  0,
		"LOAD": 1, "STORE": 2,
		"ADD": 3, "SUB": 4,
		"JMP": 5, "JZ": 6,
		"HALT": 7,
	}
	op, ok := opcodeMap[parts[0]]
	if !ok {
		return nil, fmt.Errorf("unknown opcode: %s", parts[0])
	}
	vals := []byte{0, 0, 0}
	for i := 1; i < len(parts) && i <= 3; i++ {
		n, err := strconv.Atoi(parts[i])
		if err != nil {
			return nil, fmt.Errorf("invalid operand %q: %w", parts[i], err)
		}
		vals[i-1] = byte(n)
	}
	return []byte{vals[2], vals[1], vals[0], op}, nil
}
