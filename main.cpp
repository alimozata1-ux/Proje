#include <windows.h>
#include <commdlg.h>
#include <string>
#include <sstream>
#include <iomanip>
#include <algorithm>

#pragma comment(lib, "Comdlg32.lib")

namespace {
constexpr int ID_TIMER = 1;
constexpr int ID_CLOSE_BUTTON = 1001;
constexpr int ID_COLOR_BUTTON = 1002;
constexpr int ID_ALPHA_PLUS_BUTTON = 1003;
constexpr int ID_ALPHA_MINUS_BUTTON = 1004;
constexpr int ID_PIN_BUTTON = 1005;
constexpr int ID_COPY_BUTTON = 1006;
constexpr int ID_RESET_BUTTON = 1007;

constexpr BYTE kMinAlpha = 80;
constexpr BYTE kMaxAlpha = 255;
constexpr BYTE kDefaultAlpha = 191;
constexpr COLORREF kDefaultBgColor = RGB(40, 40, 40);

HWND g_hDate = nullptr;
HWND g_hClock = nullptr;
HWND g_hCpu = nullptr;
HWND g_hRam = nullptr;
HWND g_hPin = nullptr;
COLORREF g_bgColor = kDefaultBgColor;
HBRUSH g_bgBrush = nullptr;
BYTE g_alpha = kDefaultAlpha;
bool g_isPinnedTop = true;
DWORD g_lastRamLoad = 0;
double g_lastCpuLoad = 0.0;

std::wstring GetSettingsPath() {
    wchar_t modulePath[MAX_PATH]{};
    GetModuleFileNameW(nullptr, modulePath, MAX_PATH);
    std::wstring path(modulePath);
    const auto slashPos = path.find_last_of(L"\\/");
    if (slashPos != std::wstring::npos) {
        path = path.substr(0, slashPos + 1);
    }
    return path + L"widget_settings.ini";
}

void RecreateBackgroundBrush() {
    if (g_bgBrush) {
        DeleteObject(g_bgBrush);
    }
    g_bgBrush = CreateSolidBrush(g_bgColor);
}

void ApplyAlpha(HWND hwnd) {
    SetLayeredWindowAttributes(hwnd, 0, g_alpha, LWA_ALPHA);
}

void SetPinState(HWND hwnd, bool pinTop) {
    g_isPinnedTop = pinTop;
    SetWindowPos(hwnd, g_isPinnedTop ? HWND_TOPMOST : HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE);

    if (g_hPin) {
        SetWindowTextW(g_hPin, g_isPinnedTop ? L"Sabit" : L"Normal");
    }
}

void SaveSettings(HWND hwnd) {
    const std::wstring settingsPath = GetSettingsPath();

    RECT rc{};
    GetWindowRect(hwnd, &rc);

    WritePrivateProfileStringW(L"Widget", L"PosX", std::to_wstring(rc.left).c_str(), settingsPath.c_str());
    WritePrivateProfileStringW(L"Widget", L"PosY", std::to_wstring(rc.top).c_str(), settingsPath.c_str());
    WritePrivateProfileStringW(L"Widget", L"BgColor", std::to_wstring(g_bgColor).c_str(), settingsPath.c_str());
    WritePrivateProfileStringW(L"Widget", L"Alpha", std::to_wstring(g_alpha).c_str(), settingsPath.c_str());
    WritePrivateProfileStringW(L"Widget", L"Pinned", g_isPinnedTop ? L"1" : L"0", settingsPath.c_str());
}

void LoadSettings(int& x, int& y) {
    const std::wstring settingsPath = GetSettingsPath();

    x = GetPrivateProfileIntW(L"Widget", L"PosX", 200, settingsPath.c_str());
    y = GetPrivateProfileIntW(L"Widget", L"PosY", 200, settingsPath.c_str());

    const UINT bgColorValue = GetPrivateProfileIntW(L"Widget", L"BgColor", static_cast<int>(g_bgColor), settingsPath.c_str());
    g_bgColor = static_cast<COLORREF>(bgColorValue);

    const int alphaValue = GetPrivateProfileIntW(L"Widget", L"Alpha", kDefaultAlpha, settingsPath.c_str());
    g_alpha = static_cast<BYTE>(std::clamp(alphaValue, static_cast<int>(kMinAlpha), static_cast<int>(kMaxAlpha)));

    const int pin = GetPrivateProfileIntW(L"Widget", L"Pinned", 1, settingsPath.c_str());
    g_isPinnedTop = (pin != 0);
}

void ResetWidgetDefaults(HWND hwnd) {
    g_bgColor = kDefaultBgColor;
    g_alpha = kDefaultAlpha;
    RecreateBackgroundBrush();
    ApplyAlpha(hwnd);
    SetPinState(hwnd, true);
    InvalidateRect(hwnd, nullptr, TRUE);
}

ULONGLONG FileTimeToUInt64(const FILETIME& ft) {
    return (static_cast<ULONGLONG>(ft.dwHighDateTime) << 32) | ft.dwLowDateTime;
}

double GetCpuUsagePercent() {
    static ULONGLONG prevIdle = 0;
    static ULONGLONG prevKernel = 0;
    static ULONGLONG prevUser = 0;

    FILETIME idleFt{}, kernelFt{}, userFt{};
    if (!GetSystemTimes(&idleFt, &kernelFt, &userFt)) {
        return 0.0;
    }

    const ULONGLONG idle = FileTimeToUInt64(idleFt);
    const ULONGLONG kernel = FileTimeToUInt64(kernelFt);
    const ULONGLONG user = FileTimeToUInt64(userFt);

    if (prevKernel == 0 && prevUser == 0) {
        prevIdle = idle;
        prevKernel = kernel;
        prevUser = user;
        return 0.0;
    }

    const ULONGLONG idleDiff = idle - prevIdle;
    const ULONGLONG kernelDiff = kernel - prevKernel;
    const ULONGLONG userDiff = user - prevUser;

    prevIdle = idle;
    prevKernel = kernel;
    prevUser = user;

    const ULONGLONG total = kernelDiff + userDiff;
    if (total == 0) {
        return 0.0;
    }

    return static_cast<double>(total - idleDiff) * 100.0 / static_cast<double>(total);
}

std::wstring GetRamText() {
    MEMORYSTATUSEX mem{};
    mem.dwLength = sizeof(mem);

    if (!GlobalMemoryStatusEx(&mem)) {
        g_lastRamLoad = 0;
        return L"RAM: veri alinamadi";
    }

    g_lastRamLoad = mem.dwMemoryLoad;

    const double totalGb = static_cast<double>(mem.ullTotalPhys) / (1024.0 * 1024.0 * 1024.0);
    const double usedGb = static_cast<double>(mem.ullTotalPhys - mem.ullAvailPhys) / (1024.0 * 1024.0 * 1024.0);

    std::wstringstream ss;
    ss << L"RAM: " << std::fixed << std::setprecision(1) << usedGb << L" / " << totalGb << L" GB (" << mem.dwMemoryLoad << L"%)";
    return ss.str();
}

std::wstring GetDateText() {
    SYSTEMTIME st{};
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setfill(L'0') << std::setw(2) << st.wDay << L"." << std::setw(2) << st.wMonth << L"." << st.wYear;
    return ss.str();
}

std::wstring GetClockText() {
    SYSTEMTIME st{};
    GetLocalTime(&st);

    std::wstringstream ss;
    ss << std::setfill(L'0') << std::setw(2) << st.wHour << L":" << std::setw(2) << st.wMinute << L":" << std::setw(2) << st.wSecond;
    return ss.str();
}

std::wstring GetCpuText() {
    g_lastCpuLoad = GetCpuUsagePercent();
    std::wstringstream ss;
    ss << L"CPU: " << std::fixed << std::setprecision(1) << g_lastCpuLoad << L"%";
    return ss.str();
}

std::wstring GetSnapshotText() {
    std::wstringstream ss;
    ss << GetDateText() << L" " << GetClockText() << L"\r\n" << GetCpuText() << L"\r\n" << GetRamText();
    return ss.str();
}

void CopyStatsToClipboard(HWND hwnd) {
    const std::wstring content = GetSnapshotText();
    const size_t bytes = (content.size() + 1) * sizeof(wchar_t);

    if (!OpenClipboard(hwnd)) {
        return;
    }

    EmptyClipboard();
    HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, bytes);
    if (hMem) {
        void* ptr = GlobalLock(hMem);
        if (ptr) {
            memcpy(ptr, content.c_str(), bytes);
            GlobalUnlock(hMem);
            SetClipboardData(CF_UNICODETEXT, hMem);
            hMem = nullptr;
        }
    }

    if (hMem) {
        GlobalFree(hMem);
    }

    CloseClipboard();
}

void RefreshWidgetTexts() {
    SetWindowTextW(g_hDate, GetDateText().c_str());
    SetWindowTextW(g_hClock, GetClockText().c_str());
    SetWindowTextW(g_hCpu, GetCpuText().c_str());
    SetWindowTextW(g_hRam, GetRamText().c_str());
}

void PickBackgroundColor(HWND hwnd) {
    CHOOSECOLORW cc{};
    COLORREF customColors[16] = {};

    cc.lStructSize = sizeof(cc);
    cc.hwndOwner = hwnd;
    cc.lpCustColors = customColors;
    cc.rgbResult = g_bgColor;
    cc.Flags = CC_FULLOPEN | CC_RGBINIT;

    if (ChooseColorW(&cc)) {
        g_bgColor = cc.rgbResult;
        RecreateBackgroundBrush();
        InvalidateRect(hwnd, nullptr, TRUE);
    }
}

void ChangeTransparency(HWND hwnd, int delta) {
    const int next = std::clamp(static_cast<int>(g_alpha) + delta, static_cast<int>(kMinAlpha), static_cast<int>(kMaxAlpha));
    g_alpha = static_cast<BYTE>(next);
    ApplyAlpha(hwnd);
}

COLORREF GetUsageColor(bool isCpu) {
    const double load = isCpu ? g_lastCpuLoad : static_cast<double>(g_lastRamLoad);
    if (load >= 90.0) {
        return RGB(255, 85, 85);
    }
    if (load >= 80.0) {
        return RGB(255, 186, 73);
    }
    return RGB(245, 245, 245);
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {
            g_hDate = CreateWindowW(L"STATIC", L"--.--.----", WS_CHILD | WS_VISIBLE, 16, 12, 220, 20, hwnd, nullptr, nullptr, nullptr);

            g_hClock = CreateWindowW(L"STATIC", L"--:--:--", WS_CHILD | WS_VISIBLE, 16, 34, 220, 34, hwnd, nullptr, nullptr, nullptr);

            g_hCpu = CreateWindowW(L"STATIC", L"CPU: 0%", WS_CHILD | WS_VISIBLE, 16, 76, 220, 24, hwnd, nullptr, nullptr, nullptr);

            g_hRam = CreateWindowW(L"STATIC", L"RAM: --", WS_CHILD | WS_VISIBLE, 16, 104, 300, 24, hwnd, nullptr, nullptr, nullptr);

            CreateWindowW(L"BUTTON", L"X", WS_CHILD | WS_VISIBLE | BS_OWNERDRAW, 320, 10, 36, 30, hwnd,
                          reinterpret_cast<HMENU>(ID_CLOSE_BUTTON), nullptr, nullptr);

            CreateWindowW(L"BUTTON", L"Renk", WS_CHILD | WS_VISIBLE, 16, 136, 58, 30, hwnd,
                          reinterpret_cast<HMENU>(ID_COLOR_BUTTON), nullptr, nullptr);

            CreateWindowW(L"BUTTON", L"+", WS_CHILD | WS_VISIBLE, 80, 136, 30, 30, hwnd,
                          reinterpret_cast<HMENU>(ID_ALPHA_PLUS_BUTTON), nullptr, nullptr);

            CreateWindowW(L"BUTTON", L"-", WS_CHILD | WS_VISIBLE, 114, 136, 30, 30, hwnd,
                          reinterpret_cast<HMENU>(ID_ALPHA_MINUS_BUTTON), nullptr, nullptr);

            g_hPin = CreateWindowW(L"BUTTON", g_isPinnedTop ? L"Sabit" : L"Normal", WS_CHILD | WS_VISIBLE, 148, 136, 62, 30, hwnd,
                                   reinterpret_cast<HMENU>(ID_PIN_BUTTON), nullptr, nullptr);

            CreateWindowW(L"BUTTON", L"Kopya", WS_CHILD | WS_VISIBLE, 214, 136, 60, 30, hwnd,
                          reinterpret_cast<HMENU>(ID_COPY_BUTTON), nullptr, nullptr);

            CreateWindowW(L"BUTTON", L"Sifirla", WS_CHILD | WS_VISIBLE, 278, 136, 78, 30, hwnd,
                          reinterpret_cast<HMENU>(ID_RESET_BUTTON), nullptr, nullptr);

            SendMessageW(g_hDate, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
            SendMessageW(g_hClock, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
            SendMessageW(g_hCpu, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
            SendMessageW(g_hRam, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);

            RecreateBackgroundBrush();
            ApplyAlpha(hwnd);
            SetPinState(hwnd, g_isPinnedTop);
            SetTimer(hwnd, ID_TIMER, 1000, nullptr);
            RefreshWidgetTexts();
            return 0;
        }
        case WM_LBUTTONDOWN:
            ReleaseCapture();
            SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0);
            return 0;

        case WM_TIMER:
            if (wParam == ID_TIMER) {
                RefreshWidgetTexts();
            }
            return 0;

        case WM_COMMAND: {
            const int id = LOWORD(wParam);
            if (id == ID_CLOSE_BUTTON) {
                PostMessageW(hwnd, WM_CLOSE, 0, 0);
            } else if (id == ID_COLOR_BUTTON) {
                PickBackgroundColor(hwnd);
            } else if (id == ID_ALPHA_PLUS_BUTTON) {
                ChangeTransparency(hwnd, 10);
            } else if (id == ID_ALPHA_MINUS_BUTTON) {
                ChangeTransparency(hwnd, -10);
            } else if (id == ID_PIN_BUTTON) {
                SetPinState(hwnd, !g_isPinnedTop);
            } else if (id == ID_COPY_BUTTON) {
                CopyStatsToClipboard(hwnd);
            } else if (id == ID_RESET_BUTTON) {
                ResetWidgetDefaults(hwnd);
                RefreshWidgetTexts();
            }
            return 0;
        }

        case WM_DRAWITEM: {
            auto* dis = reinterpret_cast<DRAWITEMSTRUCT*>(lParam);
            if (dis->CtlID == ID_CLOSE_BUTTON) {
                HBRUSH redBrush = CreateSolidBrush(RGB(220, 35, 35));
                FillRect(dis->hDC, &dis->rcItem, redBrush);
                DeleteObject(redBrush);

                SetBkMode(dis->hDC, TRANSPARENT);
                SetTextColor(dis->hDC, RGB(255, 255, 255));
                DrawTextW(dis->hDC, L"X", -1, &dis->rcItem, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
                return TRUE;
            }
            break;
        }

        case WM_CTLCOLORSTATIC: {
            HDC hdc = reinterpret_cast<HDC>(wParam);
            const HWND hCtrl = reinterpret_cast<HWND>(lParam);
            COLORREF textColor = RGB(245, 245, 245);

            if (hCtrl == g_hCpu) {
                textColor = GetUsageColor(true);
            } else if (hCtrl == g_hRam) {
                textColor = GetUsageColor(false);
            }

            SetTextColor(hdc, textColor);
            SetBkMode(hdc, TRANSPARENT);
            return reinterpret_cast<LRESULT>(g_bgBrush);
        }

        case WM_ERASEBKGND: {
            RECT rc;
            GetClientRect(hwnd, &rc);
            FillRect(reinterpret_cast<HDC>(wParam), &rc, g_bgBrush);
            return 1;
        }

        case WM_DESTROY:
            KillTimer(hwnd, ID_TIMER);
            SaveSettings(hwnd);
            if (g_bgBrush) {
                DeleteObject(g_bgBrush);
                g_bgBrush = nullptr;
            }
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProcW(hwnd, msg, wParam, lParam);
}
}  // namespace

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR, int nCmdShow) {
    const wchar_t CLASS_NAME[] = L"WidgetWindowClass";

    int startX = 200;
    int startY = 200;
    LoadSettings(startX, startY);

    WNDCLASSW wc{};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);

    RegisterClassW(&wc);

    HWND hwnd = CreateWindowExW(WS_EX_TOPMOST | WS_EX_LAYERED, CLASS_NAME, L"Saat / Tarih / CPU / RAM Widget", WS_POPUPWINDOW | WS_VISIBLE,
                                startX, startY, 370, 182, nullptr, nullptr, hInstance, nullptr);

    if (!hwnd) {
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);

    MSG msg{};
    while (GetMessageW(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    return 0;
}
