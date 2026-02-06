#pragma once

#include "emulator.h"
#include <windows.h>
#include <string>

class GUI {
public:
    explicit GUI(HINSTANCE hInstance);
    int run();

private:
    static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
    LRESULT handleMessage(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);

    void createControls(HWND hwnd);
    void paintBlockDiagram(HDC hdc);
    void refreshStatus();

    bool chooseAndLoad(bool hexMode);
    uint32_t parseStartAddress() const;

    HINSTANCE hInstance_;
    Emulator emulator_;

    HWND hwnd_{nullptr};
    HWND btnRun_{nullptr};
    HWND btnStep_{nullptr};
    HWND btnPause_{nullptr};
    HWND btnReset_{nullptr};
    HWND btnLoadBin_{nullptr};
    HWND btnLoadHex_{nullptr};
    HWND editStartAddr_{nullptr};
    HWND txtStatus_{nullptr};
    HWND txtRegisters_{nullptr};
    HWND txtRAM_{nullptr};
    HWND txtPins_{nullptr};

    UINT_PTR timerId_{1};
};
