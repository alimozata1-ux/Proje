#include "gui.h"
#include <windows.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE, LPSTR, int) {
    GUI app(hInstance);
    return app.run();
}
