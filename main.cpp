#include "gui.h"

// Windows uygulamaları için standart giriş noktası.
int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR, int nCmdShow) {
    GUI gui;
    if (!gui.Initialize(hInstance, nCmdShow)) {
        return -1;
    }
    return gui.RunMessageLoop();
}
