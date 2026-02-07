#pragma once

#include <string>
#include <windows.h>

#include "emulator.h"

class GUI {
public:
    GUI();

    bool Initialize(HINSTANCE hInstance, int nCmdShow);
    int RunMessageLoop();

private:
    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
    LRESULT HandleMessage(UINT uMsg, WPARAM wParam, LPARAM lParam);

    void CreateControls();
    void OnPaint();
    void DrawBlock(HDC hdc, RECT rect, const std::wstring& title);
    void UpdateStatus();

    HWND hwnd_;
    HWND btnLoad_;
    HWND btnRun_;
    HWND btnPause_;
    HWND btnStep_;
    HWND btnReset_;
    HWND btnBus16_;
    HWND btnBus32_;
    HWND btnUserButton_;
    HWND statusLabel_;

    Emulator emulator_;
    bool userButtonPressed_;
};
