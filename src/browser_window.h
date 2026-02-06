#pragma once

#include <QColor>
#include <QMainWindow>

class QAction;
class QLineEdit;
class QTabWidget;
class QToolBar;
class QWebEngineView;

class BrowserWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit BrowserWindow(QWidget* parent = nullptr);

private slots:
    void openNewTab();
    void closeTab(int index);
    void loadUrlFromAddressBar();
    void updateAddressBar(const QUrl& url);
    void openSettings();

private:
    QWebEngineView* currentView() const;
    void applyTheme();
    void loadSettings();
    void saveSettings() const;
    QWebEngineView* createTab(const QUrl& initialUrl);

    QTabWidget* m_tabWidget;
    QToolBar* m_toolbar;
    QLineEdit* m_addressBar;

    QColor m_neonColor;
    int m_chromeOpacityPercent;
    QString m_backgroundImage;
};
