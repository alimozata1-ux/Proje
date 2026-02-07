#include <chrono>
#include <csignal>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

#ifdef _WIN32
#include <windows.h>

namespace {

struct CpuSnapshot {
    ULONGLONG idle = 0;
    ULONGLONG kernel = 0;
    ULONGLONG user = 0;
};

struct Metrics {
    std::string clock;
    double cpuPercent = 0.0;
    double ramPercent = 0.0;
    unsigned long long usedRamMb = 0;
    unsigned long long totalRamMb = 0;
};

constexpr int kWidth = 460;
constexpr int kHeight = 230;
constexpr int kCloseBtnSize = 24;

Metrics g_metrics;
CpuSnapshot g_prevCpu;
HWND g_hwnd = nullptr;
bool g_hasPrevCpu = false;

RECT closeButtonRect() {
    return RECT{kWidth - 12 - kCloseBtnSize, 10, kWidth - 12, 10 + kCloseBtnSize};
}

bool parseHexColor(const char* hex, COLORREF& outColor) {
    if (!hex) return false;
    std::string s(hex);
    if (s.size() == 7 && s[0] == '#') s.erase(0, 1);
    if (s.size() != 6) return false;

    try {
        const int r = std::stoi(s.substr(0, 2), nullptr, 16);
        const int g = std::stoi(s.substr(2, 2), nullptr, 16);
        const int b = std::stoi(s.substr(4, 2), nullptr, 16);
        outColor = RGB(r, g, b);
        return true;
    } catch (...) {
        return false;
    }
}

std::string currentTimeString() {
    auto now = std::chrono::system_clock::now();
    std::time_t tt = std::chrono::system_clock::to_time_t(now);
    std::tm tm{};
    localtime_s(&tm, &tt);

    std::ostringstream oss;
    oss << std::put_time(&tm, "%d.%m.%Y %H:%M:%S");
    return oss.str();
}

ULONGLONG fileTimeToULL(const FILETIME& ft) {
    ULARGE_INTEGER ui;
    ui.LowPart = ft.dwLowDateTime;
    ui.HighPart = ft.dwHighDateTime;
    return ui.QuadPart;
}

bool readCpuSnapshot(CpuSnapshot& out) {
    FILETIME idleTime{}, kernelTime{}, userTime{};
    if (!GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
        return false;
    }
    out.idle = fileTimeToULL(idleTime);
    out.kernel = fileTimeToULL(kernelTime);
    out.user = fileTimeToULL(userTime);
    return true;
}

double cpuUsagePercent(const CpuSnapshot& prev, const CpuSnapshot& cur) {
    const ULONGLONG idleDelta = cur.idle - prev.idle;
    const ULONGLONG kernelDelta = cur.kernel - prev.kernel;
    const ULONGLONG userDelta = cur.user - prev.user;
    const ULONGLONG total = kernelDelta + userDelta;
    if (total == 0) return 0.0;
    return 100.0 * static_cast<double>(total - idleDelta) / static_cast<double>(total);
}

bool readRamUsage(Metrics& m) {
    MEMORYSTATUSEX state{};
    state.dwLength = sizeof(state);
    if (!GlobalMemoryStatusEx(&state)) {
        return false;
    }

    const unsigned long long total = state.ullTotalPhys;
    const unsigned long long avail = state.ullAvailPhys;
    const unsigned long long used = total - avail;

    m.totalRamMb = total / (1024ull * 1024ull);
    m.usedRamMb = used / (1024ull * 1024ull);
    m.ramPercent = total ? (100.0 * static_cast<double>(used) / static_cast<double>(total)) : 0.0;
    return true;
}

void updateMetrics() {
    g_metrics.clock = currentTimeString();

    CpuSnapshot cur{};
    if (readCpuSnapshot(cur)) {
        if (g_hasPrevCpu) {
            g_metrics.cpuPercent = cpuUsagePercent(g_prevCpu, cur);
            if (g_metrics.cpuPercent < 0.0) g_metrics.cpuPercent = 0.0;
            if (g_metrics.cpuPercent > 100.0) g_metrics.cpuPercent = 100.0;
        }
        g_prevCpu = cur;
        g_hasPrevCpu = true;
    }

    readRamUsage(g_metrics);
}

void drawBar(HDC hdc, int x, int y, int w, int h, double percent, COLORREF fill, COLORREF border) {
    if (percent < 0.0) percent = 0.0;
    if (percent > 100.0) percent = 100.0;

    HBRUSH bg = CreateSolidBrush(RGB(30, 41, 59));
    RECT r{x, y, x + w, y + h};
    FillRect(hdc, &r, bg);
    DeleteObject(bg);

    const int fillW = static_cast<int>((w - 2) * (percent / 100.0));
    HBRUSH fb = CreateSolidBrush(fill);
    RECT fr{x + 1, y + 1, x + 1 + fillW, y + h - 1};
    FillRect(hdc, &fr, fb);
    DeleteObject(fb);

    HPEN pen = CreatePen(PS_SOLID, 1, border);
    HGDIOBJ oldPen = SelectObject(hdc, pen);
    HGDIOBJ oldBrush = SelectObject(hdc, GetStockObject(NULL_BRUSH));
    Rectangle(hdc, x, y, x + w, y + h);
    SelectObject(hdc, oldBrush);
    SelectObject(hdc, oldPen);
    DeleteObject(pen);
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static COLORREF bgColor = RGB(30, 41, 59);

    switch (msg) {
        case WM_CREATE: {
            const char* envColor = std::getenv("WIDGET_BG_COLOR");
            parseHexColor(envColor, bgColor);

            SetLayeredWindowAttributes(hwnd, 0, static_cast<BYTE>(191), LWA_ALPHA); // ~75%
            SetTimer(hwnd, 1, 1000, nullptr);
            updateMetrics();
            return 0;
        }
        case WM_TIMER:
            updateMetrics();
            InvalidateRect(hwnd, nullptr, TRUE);
            return 0;
        case WM_LBUTTONDOWN: {
            const int x = GET_X_LPARAM(lParam);
            const int y = GET_Y_LPARAM(lParam);
            RECT c = closeButtonRect();
            if (x >= c.left && x <= c.right && y >= c.top && y <= c.bottom) {
                DestroyWindow(hwnd);
            }
            return 0;
        }
        case WM_PAINT: {
            PAINTSTRUCT ps{};
            HDC hdc = BeginPaint(hwnd, &ps);

            HBRUSH bg = CreateSolidBrush(bgColor);
            RECT client{};
            GetClientRect(hwnd, &client);
            FillRect(hdc, &client, bg);
            DeleteObject(bg);

            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, RGB(248, 250, 252));

            HFONT font = CreateFontA(18, 0, 0, 0, FW_SEMIBOLD, FALSE, FALSE, FALSE,
                                     DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                     CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_SWISS, "Segoe UI");
            HGDIOBJ oldFont = SelectObject(hdc, font);

            TextOutA(hdc, 16, 22, "Saat", 4);
            TextOutA(hdc, 16, 48, g_metrics.clock.c_str(), static_cast<int>(g_metrics.clock.size()));

            std::ostringstream cpu;
            cpu << "CPU: " << std::fixed << std::setprecision(1) << g_metrics.cpuPercent << "%";
            const std::string cpuText = cpu.str();
            TextOutA(hdc, 16, 88, cpuText.c_str(), static_cast<int>(cpuText.size()));
            drawBar(hdc, 16, 110, kWidth - 32, 18, g_metrics.cpuPercent, RGB(34, 211, 238), RGB(148, 163, 184));

            std::ostringstream ram;
            ram << "RAM: " << std::fixed << std::setprecision(1) << g_metrics.ramPercent << "% ("
                << g_metrics.usedRamMb << " / " << g_metrics.totalRamMb << " MB)";
            const std::string ramText = ram.str();
            TextOutA(hdc, 16, 148, ramText.c_str(), static_cast<int>(ramText.size()));
            drawBar(hdc, 16, 170, kWidth - 32, 18, g_metrics.ramPercent, RGB(96, 165, 250), RGB(148, 163, 184));

            RECT c = closeButtonRect();
            HBRUSH red = CreateSolidBrush(RGB(255, 0, 0));
            FillRect(hdc, &c, red);
            DeleteObject(red);
            SetTextColor(hdc, RGB(255, 255, 255));
            TextOutA(hdc, c.left + 8, c.top + 4, "X", 1);

            SelectObject(hdc, oldFont);
            DeleteObject(font);
            EndPaint(hwnd, &ps);
            return 0;
        }
        case WM_DESTROY:
            KillTimer(hwnd, 1);
            PostQuitMessage(0);
            return 0;
    }

    return DefWindowProc(hwnd, msg, wParam, lParam);
}

}  // namespace

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR, int) {
    const char* clsName = "SystemWidgetWin32";

    WNDCLASSA wc{};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = clsName;
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    RegisterClassA(&wc);

    g_hwnd = CreateWindowExA(
        WS_EX_LAYERED | WS_EX_TOPMOST,
        clsName,
        "Saat + CPU + RAM Widget",
        WS_POPUP | WS_VISIBLE,
        80, 80, kWidth, kHeight,
        nullptr, nullptr, hInstance, nullptr);

    if (!g_hwnd) {
        return 1;
    }

    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}

#else

int main() {
    std::cerr << "Bu surum Windows uygulamasi olarak yazildi. Lutfen Windows'ta derleyin/calistirin.\n";
    return 1;
}

#endif
