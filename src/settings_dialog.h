#pragma once

#include <QColor>
#include <QDialog>

class QPushButton;
class QSlider;

class SettingsDialog : public QDialog {
    Q_OBJECT

public:
    explicit SettingsDialog(const QColor& neonColor, int opacityPercent, QWidget* parent = nullptr);

    QColor selectedNeonColor() const;
    int selectedOpacityPercent() const;
    QString selectedBackgroundImage() const;

private slots:
    void pickNeonColor();
    void pickBackgroundImage();

private:
    void updatePreviewButton();

    QColor m_neonColor;
    int m_opacityPercent;
    QString m_backgroundImage;

    QPushButton* m_colorButton;
    QSlider* m_opacitySlider;
    QPushButton* m_backgroundButton;
};
