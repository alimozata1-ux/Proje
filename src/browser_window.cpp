#include "browser_window.h"

#include "settings_dialog.h"

#include <QAction>
#include <algorithm>
#include <QFileInfo>
#include <QLineEdit>
#include <QMenuBar>
#include <QSettings>
#include <QStatusBar>
#include <QTabBar>
#include <QTabWidget>
#include <QToolBar>
#include <QUrl>
#include <QVBoxLayout>
#include <QWebEngineView>

namespace {
constexpr auto kSettingsGroup = "neon_browser";
}

BrowserWindow::BrowserWindow(QWidget* parent)
    : QMainWindow(parent),
      m_tabWidget(new QTabWidget(this)),
      m_toolbar(new QToolBar(tr("Araç Çubuğu"), this)),
      m_addressBar(new QLineEdit(this)),
      m_neonColor(0, 255, 255),
      m_chromeOpacityPercent(75) {
    setWindowTitle(tr("Neon Browser"));
    resize(1280, 820);

    m_tabWidget->setDocumentMode(true);
    m_tabWidget->setTabsClosable(true);
    setCentralWidget(m_tabWidget);

    connect(m_tabWidget, &QTabWidget::tabCloseRequested, this, &BrowserWindow::closeTab);
    connect(m_tabWidget, &QTabWidget::currentChanged, this, [this](int) {
        if (auto* view = currentView()) {
            m_addressBar->setText(view->url().toString());
        }
    });

    addToolBar(m_toolbar);
    m_toolbar->setMovable(false);

    auto* back = m_toolbar->addAction(tr("←"));
    auto* forward = m_toolbar->addAction(tr("→"));
    auto* reload = m_toolbar->addAction(tr("⟳"));
    auto* newTab = m_toolbar->addAction(tr("+ Sekme"));

    m_addressBar->setPlaceholderText(tr("Adres yaz: https://...") );
    m_addressBar->setClearButtonEnabled(true);
    m_toolbar->addWidget(m_addressBar);

    connect(back, &QAction::triggered, this, [this]() {
        if (auto* view = currentView()) {
            view->back();
        }
    });
    connect(forward, &QAction::triggered, this, [this]() {
        if (auto* view = currentView()) {
            view->forward();
        }
    });
    connect(reload, &QAction::triggered, this, [this]() {
        if (auto* view = currentView()) {
            view->reload();
        }
    });
    connect(newTab, &QAction::triggered, this, &BrowserWindow::openNewTab);
    connect(m_addressBar, &QLineEdit::returnPressed, this, &BrowserWindow::loadUrlFromAddressBar);

    auto* settingsAction = menuBar()->addAction(tr("Ayarlar"));
    connect(settingsAction, &QAction::triggered, this, &BrowserWindow::openSettings);

    loadSettings();
    createTab(QUrl("https://www.qt.io"));
    applyTheme();
    statusBar()->showMessage(tr("Neon tema aktif."));
}

void BrowserWindow::openNewTab() {
    createTab(QUrl("https://duckduckgo.com"));
}

void BrowserWindow::closeTab(int index) {
    if (m_tabWidget->count() == 1) {
        close();
        return;
    }

    QWidget* page = m_tabWidget->widget(index);
    m_tabWidget->removeTab(index);
    delete page;
}

void BrowserWindow::loadUrlFromAddressBar() {
    if (auto* view = currentView()) {
        QUrl url = QUrl::fromUserInput(m_addressBar->text().trimmed());
        if (!url.isValid()) {
            return;
        }
        view->setUrl(url);
    }
}

void BrowserWindow::updateAddressBar(const QUrl& url) {
    if (auto* view = qobject_cast<QWebEngineView*>(sender()); view == currentView()) {
        m_addressBar->setText(url.toString());
    }
}

void BrowserWindow::openSettings() {
    SettingsDialog dialog(m_neonColor, m_chromeOpacityPercent, this);
    if (dialog.exec() == QDialog::Accepted) {
        m_neonColor = dialog.selectedNeonColor();
        m_chromeOpacityPercent = dialog.selectedOpacityPercent();
        if (!dialog.selectedBackgroundImage().isEmpty()) {
            m_backgroundImage = dialog.selectedBackgroundImage();
        }
        applyTheme();
        saveSettings();
    }
}

QWebEngineView* BrowserWindow::currentView() const {
    return qobject_cast<QWebEngineView*>(m_tabWidget->currentWidget());
}

void BrowserWindow::applyTheme() {
    const int alpha = std::clamp(static_cast<int>(255.0 * (m_chromeOpacityPercent / 100.0)), 0, 255);
    const QString neonRgb = QString("%1, %2, %3").arg(m_neonColor.red()).arg(m_neonColor.green()).arg(m_neonColor.blue());

    QString appStyle = QString(R"(
        QMainWindow {
            background-color: rgb(8, 8, 16);
            color: rgb(%1);
        }
        QToolBar, QTabBar::tab {
            background-color: rgba(20, 20, 30, %2);
            border: 1px solid rgba(%1, 220);
            color: rgba(%1, 255);
        }
        QLineEdit {
            background-color: rgba(10, 10, 15, %2);
            color: rgba(%1, 255);
            border: 1px solid rgba(%1, 255);
            border-radius: 6px;
            padding: 6px;
        }
        QTabBar::tab:selected {
            background-color: rgba(%1, %2);
            color: black;
        }
        QMenuBar {
            background-color: rgba(20, 20, 30, %2);
            color: rgba(%1, 255);
        }
    )")
                           .arg(neonRgb)
                           .arg(alpha);

    if (!m_backgroundImage.isEmpty() && QFileInfo::exists(m_backgroundImage)) {
        appStyle += QString("QMainWindow { border-image: url('%1') 0 0 0 0 stretch stretch; }").arg(m_backgroundImage);
    }

    setStyleSheet(appStyle);
}

void BrowserWindow::loadSettings() {
    QSettings settings;
    settings.beginGroup(kSettingsGroup);
    m_neonColor = settings.value("neonColor", QColor(0, 255, 255)).value<QColor>();
    m_chromeOpacityPercent = settings.value("chromeOpacityPercent", 75).toInt();
    m_backgroundImage = settings.value("backgroundImage", QString()).toString();
    settings.endGroup();
}

void BrowserWindow::saveSettings() const {
    QSettings settings;
    settings.beginGroup(kSettingsGroup);
    settings.setValue("neonColor", m_neonColor);
    settings.setValue("chromeOpacityPercent", m_chromeOpacityPercent);
    settings.setValue("backgroundImage", m_backgroundImage);
    settings.endGroup();
}

QWebEngineView* BrowserWindow::createTab(const QUrl& initialUrl) {
    auto* view = new QWebEngineView(m_tabWidget);
    const int index = m_tabWidget->addTab(view, tr("Yeni Sekme"));
    m_tabWidget->setCurrentIndex(index);

    connect(view, &QWebEngineView::urlChanged, this, &BrowserWindow::updateAddressBar);
    connect(view, &QWebEngineView::titleChanged, this, [this, view](const QString& title) {
        const int idx = m_tabWidget->indexOf(view);
        if (idx >= 0) {
            m_tabWidget->setTabText(idx, title.left(18));
        }
    });

    view->setUrl(initialUrl);
    return view;
}
