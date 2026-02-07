#include "gui.h"
#include <windows.h>

namespace {
int RunGuiApp(HINSTANCE hInstance) {
    GUI app(hInstance);
    return app.run();
}
}

// Windows GUI entry point
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR, int) {
    return RunGuiApp(hInstance);
}

// Optional standard entry point.
// This makes project templates/tools that expect `main` happy,
// while still supporting WinAPI GUI startup.
int main() {
    return RunGuiApp(GetModuleHandle(nullptr));
}
