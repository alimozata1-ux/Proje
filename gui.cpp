#include "gui.h"
#include <commdlg.h>
#include <iomanip>
#include <sstream>

namespace {
constexpr int ID_RUN = 1001;
constexpr int ID_STEP = 1002;
constexpr int ID_PAUSE = 1003;
constexpr int ID_RESET = 1004;
constexpr int ID_LOAD_BIN = 1005;
constexpr int ID_LOAD_HEX = 1006;
}

GUI::GUI(HINSTANCE hInstance) : hInstance_(hInstance), emulator_() {}

int GUI::run() {
    WNDCLASS wc{};
    wc.lpfnWndProc = GUI::WndProc;
    wc.hInstance = hInstance_;
    wc.lpszClassName = TEXT("McuEmuWnd");
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);

    RegisterClass(&wc);

    hwnd_ = CreateWindowEx(
        0, wc.lpszClassName, TEXT("MCU Architecture Designer & Emulator"),
        WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 1100, 760,
        nullptr, nullptr, hInstance_, this
    );

    ShowWindow(hwnd_, SW_SHOW);
    UpdateWindow(hwnd_);

    SetTimer(hwnd_, timerId_, 30, nullptr);

    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    return static_cast<int>(msg.wParam);
}

LRESULT CALLBACK GUI::WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    GUI* self = nullptr;
    if (msg == WM_NCCREATE) {
        auto* cs = reinterpret_cast<CREATESTRUCT*>(lParam);
        self = reinterpret_cast<GUI*>(cs->lpCreateParams);
        SetWindowLongPtr(hwnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(self));
        self->hwnd_ = hwnd;
    } else {
        self = reinterpret_cast<GUI*>(GetWindowLongPtr(hwnd, GWLP_USERDATA));
    }

    if (self) return self->handleMessage(hwnd, msg, wParam, lParam);
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

LRESULT GUI::handleMessage(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
    case WM_CREATE:
        createControls(hwnd);
        refreshStatus();
        return 0;
    case WM_COMMAND: {
        switch (LOWORD(wParam)) {
        case ID_RUN:
            emulator_.run(true);
            break;
        case ID_STEP:
            emulator_.step();
            break;
        case ID_PAUSE:
            emulator_.pause();
            break;
        case ID_RESET:
            emulator_.reset(parseStartAddress());
            break;
        case ID_LOAD_BIN:
            chooseAndLoad(false);
            break;
        case ID_LOAD_HEX:
            chooseAndLoad(true);
            break;
        default:
            break;
        }
        refreshStatus();
        InvalidateRect(hwnd, nullptr, TRUE);
        return 0;
    }
    case WM_TIMER:
        emulator_.tickFrame(20);
        refreshStatus();
        InvalidateRect(hwnd, nullptr, FALSE);
        return 0;
    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);
        paintBlockDiagram(hdc);
        EndPaint(hwnd, &ps);
        return 0;
    }
    case WM_DESTROY:
        KillTimer(hwnd, timerId_);
        PostQuitMessage(0);
        return 0;
    default:
        return DefWindowProc(hwnd, msg, wParam, lParam);
    }
}

void GUI::createControls(HWND hwnd) {
    btnRun_ = CreateWindow(TEXT("BUTTON"), TEXT("Run"), WS_VISIBLE | WS_CHILD,
        20, 20, 90, 30, hwnd, reinterpret_cast<HMENU>(ID_RUN), hInstance_, nullptr);
    btnStep_ = CreateWindow(TEXT("BUTTON"), TEXT("Step"), WS_VISIBLE | WS_CHILD,
        120, 20, 90, 30, hwnd, reinterpret_cast<HMENU>(ID_STEP), hInstance_, nullptr);
    btnPause_ = CreateWindow(TEXT("BUTTON"), TEXT("Pause"), WS_VISIBLE | WS_CHILD,
        220, 20, 90, 30, hwnd, reinterpret_cast<HMENU>(ID_PAUSE), hInstance_, nullptr);
    btnReset_ = CreateWindow(TEXT("BUTTON"), TEXT("Reset"), WS_VISIBLE | WS_CHILD,
        320, 20, 90, 30, hwnd, reinterpret_cast<HMENU>(ID_RESET), hInstance_, nullptr);
    btnLoadBin_ = CreateWindow(TEXT("BUTTON"), TEXT("Load BIN"), WS_VISIBLE | WS_CHILD,
        420, 20, 100, 30, hwnd, reinterpret_cast<HMENU>(ID_LOAD_BIN), hInstance_, nullptr);
    btnLoadHex_ = CreateWindow(TEXT("BUTTON"), TEXT("Load HEX"), WS_VISIBLE | WS_CHILD,
        530, 20, 100, 30, hwnd, reinterpret_cast<HMENU>(ID_LOAD_HEX), hInstance_, nullptr);

    CreateWindow(TEXT("STATIC"), TEXT("Start Addr (hex):"), WS_VISIBLE | WS_CHILD,
        650, 25, 120, 20, hwnd, nullptr, hInstance_, nullptr);
    editStartAddr_ = CreateWindow(TEXT("EDIT"), TEXT("0x0000"), WS_VISIBLE | WS_CHILD | WS_BORDER,
        780, 22, 120, 24, hwnd, nullptr, hInstance_, nullptr);

    txtStatus_ = CreateWindow(TEXT("STATIC"), TEXT(""), WS_VISIBLE | WS_CHILD,
        20, 60, 1000, 20, hwnd, nullptr, hInstance_, nullptr);

    txtRegisters_ = CreateWindow(TEXT("STATIC"), TEXT(""), WS_VISIBLE | WS_CHILD,
        20, 380, 500, 160, hwnd, nullptr, hInstance_, nullptr);
    txtRAM_ = CreateWindow(TEXT("STATIC"), TEXT(""), WS_VISIBLE | WS_CHILD,
        20, 550, 700, 140, hwnd, nullptr, hInstance_, nullptr);
    txtPins_ = CreateWindow(TEXT("STATIC"), TEXT(""), WS_VISIBLE | WS_CHILD,
        540, 380, 500, 80, hwnd, nullptr, hInstance_, nullptr);
}

void GUI::paintBlockDiagram(HDC hdc) {
    RECT r;
    GetClientRect(hwnd_, &r);

    SetBkMode(hdc, TRANSPARENT);
    Rectangle(hdc, 20, 100, 240, 220); TextOut(hdc, 30, 110, TEXT("CPU Core"), 8);
    Rectangle(hdc, 260, 100, 480, 220); TextOut(hdc, 270, 110, TEXT("ROM / Flash"), 11);
    Rectangle(hdc, 500, 100, 720, 220); TextOut(hdc, 510, 110, TEXT("RAM"), 3);
    Rectangle(hdc, 740, 100, 960, 220); TextOut(hdc, 750, 110, TEXT("GPIO / Pins"), 11);
    Rectangle(hdc, 20, 240, 240, 340); TextOut(hdc, 30, 250, TEXT("Clock & Power"), 13);
    Rectangle(hdc, 260, 240, 480, 340); TextOut(hdc, 270, 250, TEXT("Timer"), 5);
    Rectangle(hdc, 500, 240, 720, 340); TextOut(hdc, 510, 250, TEXT("Interrupt Ctrl"), 14);
    Rectangle(hdc, 740, 240, 960, 340); TextOut(hdc, 750, 250, TEXT("UART"), 4);

    MoveToEx(hdc, 240, 160, nullptr); LineTo(hdc, 260, 160);
    MoveToEx(hdc, 480, 160, nullptr); LineTo(hdc, 500, 160);
    MoveToEx(hdc, 720, 160, nullptr); LineTo(hdc, 740, 160);

    std::wstringstream wss;
    wss << L"Active Instr: ";
    auto inst = emulator_.mcu().cpu.lastInstructionText();
    wss << std::wstring(inst.begin(), inst.end());
    auto text = wss.str();
    TextOutW(hdc, 20, 350, text.c_str(), static_cast<int>(text.size()));
}

uint32_t GUI::parseStartAddress() const {
    char buf[64] = {0};
    GetWindowTextA(editStartAddr_, buf, sizeof(buf));
    std::string s(buf);
    try {
        return static_cast<uint32_t>(std::stoul(s, nullptr, 0));
    } catch (...) {
        return 0;
    }
}

bool GUI::chooseAndLoad(bool hexMode) {
    char fileName[MAX_PATH] = {0};
    OPENFILENAMEA ofn{};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd_;
    ofn.lpstrFile = fileName;
    ofn.nMaxFile = MAX_PATH;
    ofn.lpstrFilter = hexMode
        ? "HEX Files\0*.hex\0All Files\0*.*\0"
        : "BIN Files\0*.bin\0All Files\0*.*\0";
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;

    if (!GetOpenFileNameA(&ofn)) return false;

    std::string error;
    uint32_t start = parseStartAddress();
    bool ok = hexMode
        ? emulator_.loadProgramHex(fileName, start, error)
        : emulator_.loadProgramBin(fileName, start, error);

    if (!ok) {
        MessageBoxA(hwnd_, error.c_str(), "Load Error", MB_ICONERROR);
    }
    return ok;
}

void GUI::refreshStatus() {
    const auto& mcu = emulator_.mcu();

    std::ostringstream s;
    s << "PC=0x" << std::hex << mcu.cpu.pc()
      << "  CYCLES=" << std::dec << mcu.clock.cycles()
      << "  RUNNING=" << (emulator_.isRunning() ? "YES" : "NO")
      << "  HALTED=" << (mcu.cpu.halted() ? "YES" : "NO")
      << "  ZF=" << (mcu.cpu.zeroFlag() ? 1 : 0);
    SetWindowTextA(txtStatus_, s.str().c_str());

    std::ostringstream reg;
    reg << "Registers:\n";
    for (std::size_t i = 0; i < mcu.cpu.registers().size(); ++i) {
        reg << "R" << i << "=0x" << std::hex << mcu.cpu.registers()[i] << "  ";
        if ((i + 1) % 4 == 0) reg << "\n";
    }
    SetWindowTextA(txtRegisters_, reg.str().c_str());

    std::ostringstream ram;
    ram << "RAM[0x0000..0x003F]:\n";
    for (int i = 0; i < 64; ++i) {
        uint8_t v = 0;
        mcu.ram.read(i, v);
        ram << std::setw(2) << std::setfill('0') << std::hex << +v << ' ';
        if ((i + 1) % 16 == 0) ram << "\n";
    }
    SetWindowTextA(txtRAM_, ram.str().c_str());

    std::ostringstream pins;
    pins << "Pins: ";
    for (std::size_t i = 0; i < mcu.pins.count(); ++i) {
        pins << "P" << i << '=' << (mcu.pins.read(i) ? '1' : '0') << ' ';
    }
    SetWindowTextA(txtPins_, pins.str().c_str());
}
