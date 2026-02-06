#include "browser_window.h"

#include <QApplication>
#include <QCoreApplication>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    QCoreApplication::setOrganizationName("NeonLab");
    QCoreApplication::setApplicationName("NeonBrowser");

    BrowserWindow window;
    window.show();

    return app.exec();
}
