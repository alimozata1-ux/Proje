//go:build !windows

package main

import "fmt"

func main() {
	fmt.Println("Neon Browser şu anda yalnızca Windows üzerinde çalışır. EXE için build_windows.bat kullanın.")
}
