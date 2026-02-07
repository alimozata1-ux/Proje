#include "gui.h"

#include <commdlg.h>
#include <sstream>

namespace {
constexpr UINT_PTR kTimerId = 1;
constexpr UINT kTimerMs = 120;

constexpr int ID_BTN_LOAD = 1001;
constexpr int ID_BTN_RUN = 1002;
constexpr int ID_BTN_PAUSE = 1003;
constexpr int ID_BTN_STEP = 1004;
constexpr int ID_BTN_RESET = 1005;
constexpr int ID_RADIO_16 = 1006;
constexpr int ID_RADIO_32 = 1007;
constexpr int ID_BTN_USER = 1008;
}

GUI::GUI()
    : hwnd_(nullptr), btnLoad_(nullptr), btnRun_(nullptr), btnPause_(nullptr), btnStep_(nullptr),
      btnReset_(nullptr), btnBus16_(nullptr), btnBus32_(nullptr), btnUserButton_(nullptr),
      statusLabel_(nullptr), emulator_(), userButtonPressed_(false) {}

bool GUI::Initialize(HINSTANCE hInstance, int nCmdShow) {
    const wchar_t CLASS_NAME[] = L"McuEmuWindowClass";

    WNDCLASS wc = {};
    wc.lpfnWndProc = GUI::WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);

    RegisterClass(&wc);

    hwnd_ = CreateWindowEx(
        0,
        CLASS_NAME,
        L"MCU Emulator (MVC - C++17 - MSVC)",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 980, 680,
        nullptr,
        nullptr,
        hInstance,
        this);

    if (!hwnd_) {
        return false;
    }

    ShowWindow(hwnd_, nCmdShow);
    UpdateWindow(hwnd_);
    SetTimer(hwnd_, kTimerId, kTimerMs, nullptr);
    return true;
}

int GUI::RunMessageLoop() {
    MSG msg = {};
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return static_cast<int>(msg.wParam);
}

LRESULT CALLBACK GUI::WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    GUI* self = nullptr;

    if (uMsg == WM_NCCREATE) {
        auto* cs = reinterpret_cast<CREATESTRUCT*>(lParam);
        self = reinterpret_cast<GUI*>(cs->lpCreateParams);
        SetWindowLongPtr(hwnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(self));
        self->hwnd_ = hwnd;
    } else {
        self = reinterpret_cast<GUI*>(GetWindowLongPtr(hwnd, GWLP_USERDATA));
    }

    if (self) {
        return self->HandleMessage(uMsg, wParam, lParam);
    }

    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

LRESULT GUI::HandleMessage(UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
    case WM_CREATE:
        CreateControls();
        UpdateStatus();
        return 0;

    case WM_COMMAND: {
        const int id = LOWORD(wParam);
        if (id == ID_BTN_LOAD) {
            OPENFILENAME ofn = {};
            char fileName[MAX_PATH] = {};
            ofn.lStructSize = sizeof(ofn);
            ofn.hwndOwner = hwnd_;
            ofn.lpstrFilter = "Program Files\0*.c;*.hex;*.bin\0All Files\0*.*\0";
            ofn.lpstrFile = fileName;
            ofn.nMaxFile = MAX_PATH;
            ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;

            if (GetOpenFileName(&ofn)) {
                std::string error;
                if (!emulator_.LoadProgram(fileName, error)) {
                    MessageBoxA(hwnd_, error.c_str(), "Load Error", MB_ICONERROR);
                }
            }
        } else if (id == ID_BTN_RUN) {
            emulator_.Run();
        } else if (id == ID_BTN_PAUSE) {
            emulator_.Pause();
        } else if (id == ID_BTN_STEP) {
            emulator_.Step();
        } else if (id == ID_BTN_RESET) {
            emulator_.Reset();
        } else if (id == ID_RADIO_16) {
            emulator_.SetBusWidth(BusWidth::Bit16);
            SendMessage(btnBus16_, BM_SETCHECK, BST_CHECKED, 0);
            SendMessage(btnBus32_, BM_SETCHECK, BST_UNCHECKED, 0);
        } else if (id == ID_RADIO_32) {
            emulator_.SetBusWidth(BusWidth::Bit32);
            SendMessage(btnBus16_, BM_SETCHECK, BST_UNCHECKED, 0);
            SendMessage(btnBus32_, BM_SETCHECK, BST_CHECKED, 0);
        } else if (id == ID_BTN_USER) {
            userButtonPressed_ = !userButtonPressed_;
            emulator_.SetButtonState(0, userButtonPressed_);
            SetWindowText(btnUserButton_, userButtonPressed_ ? L"Button: ON" : L"Button: OFF");
        }

        UpdateStatus();
        InvalidateRect(hwnd_, nullptr, TRUE);
        return 0;
    }

    case WM_TIMER:
        if (wParam == kTimerId && emulator_.IsRunning()) {
            emulator_.Step();
            UpdateStatus();
            InvalidateRect(hwnd_, nullptr, TRUE);
        }
        return 0;

    case WM_PAINT:
        OnPaint();
        return 0;

    case WM_DESTROY:
        KillTimer(hwnd_, kTimerId);
        PostQuitMessage(0);
        return 0;
    }

    return DefWindowProc(hwnd_, uMsg, wParam, lParam);
}

void GUI::CreateControls() {
    btnLoad_ = CreateWindow(L"BUTTON", L"Load (.c/.hex/.bin)", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
        20, 20, 170, 30, hwnd_, reinterpret_cast<HMENU>(ID_BTN_LOAD), nullptr, nullptr);

    btnRun_ = CreateWindow(L"BUTTON", L"Run", WS_TABSTOP | WS_VISIBLE | WS_CHILD,
        210, 20, 80, 30, hwnd_, reinterpret_cast<HMENU>(ID_BTN_RUN), nullptr, nullptr);

    btnPause_ = CreateWindow(L"BUTTON", L"Pause", WS_TABSTOP | WS_VISIBLE | WS_CHILD,
        300, 20, 80, 30, hwnd_, reinterpret_cast<HMENU>(ID_BTN_PAUSE), nullptr, nullptr);

    btnStep_ = CreateWindow(L"BUTTON", L"Step", WS_TABSTOP | WS_VISIBLE | WS_CHILD,
        390, 20, 80, 30, hwnd_, reinterpret_cast<HMENU>(ID_BTN_STEP), nullptr, nullptr);

    btnReset_ = CreateWindow(L"BUTTON", L"Reset", WS_TABSTOP | WS_VISIBLE | WS_CHILD,
        480, 20, 80, 30, hwnd_, reinterpret_cast<HMENU>(ID_BTN_RESET), nullptr, nullptr);

    btnBus16_ = CreateWindow(L"BUTTON", L"16-bit Bus", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_AUTORADIOBUTTON,
        590, 20, 110, 30, hwnd_, reinterpret_cast<HMENU>(ID_RADIO_16), nullptr, nullptr);

    btnBus32_ = CreateWindow(L"BUTTON", L"32-bit Bus", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_AUTORADIOBUTTON,
        710, 20, 110, 30, hwnd_, reinterpret_cast<HMENU>(ID_RADIO_32), nullptr, nullptr);

    btnUserButton_ = CreateWindow(L"BUTTON", L"Button: OFF", WS_TABSTOP | WS_VISIBLE | WS_CHILD,
        830, 20, 120, 30, hwnd_, reinterpret_cast<HMENU>(ID_BTN_USER), nullptr, nullptr);

    statusLabel_ = CreateWindow(L"STATIC", L"Status", WS_VISIBLE | WS_CHILD,
        20, 60, 930, 25, hwnd_, nullptr, nullptr, nullptr);

    SendMessage(btnBus16_, BM_SETCHECK, BST_CHECKED, 0);
}

void GUI::OnPaint() {
    PAINTSTRUCT ps;
    HDC hdc = BeginPaint(hwnd_, &ps);

    RECT ramRect{40, 120, 220, 200};
    RECT regRect{260, 120, 440, 200};
    RECT pinRect{480, 120, 660, 200};
    RECT clkRect{700, 120, 880, 200};
    RECT pwrRect{40, 230, 220, 310};

    DrawBlock(hdc, ramRect, L"RAM");
    DrawBlock(hdc, regRect, L"Registers/CPU");
    DrawBlock(hdc, pinRect, L"Pins/IO");
    DrawBlock(hdc, clkRect, L"Clock");
    DrawBlock(hdc, pwrRect, L"Power");

    // LED göstergeleri
    TextOut(hdc, 40, 340, L"LEDs:", 5);
    for (int i = 0; i < 8; ++i) {
        const bool on = emulator_.GetLedState(i);
        HBRUSH brush = CreateSolidBrush(on ? RGB(0, 220, 0) : RGB(60, 60, 60));
        HBRUSH old = (HBRUSH)SelectObject(hdc, brush);
        Ellipse(hdc, 40 + i * 35, 370, 65 + i * 35, 395);
        SelectObject(hdc, old);
        DeleteObject(brush);
    }

    // Basit ekran (7-segment yerine hexadecimal yazım)
    RECT screenRect{40, 420, 400, 500};
    Rectangle(hdc, screenRect.left, screenRect.top, screenRect.right, screenRect.bottom);
    const uint32_t screen = emulator_.GetScreenValue();
    std::wstringstream wss;
    wss << L"SCREEN: 0x" << std::hex << screen;
    const std::wstring text = wss.str();
    TextOut(hdc, 55, 450, text.c_str(), static_cast<int>(text.size()));

    EndPaint(hwnd_, &ps);
}

void GUI::DrawBlock(HDC hdc, RECT rect, const std::wstring& title) {
    Rectangle(hdc, rect.left, rect.top, rect.right, rect.bottom);
    TextOut(hdc, rect.left + 10, rect.top + 10, title.c_str(), static_cast<int>(title.size()));
}

void GUI::UpdateStatus() {
    const std::string status = emulator_.GetStatusText();
    SetWindowTextA(statusLabel_, status.c_str());
}
