#include "settings_dialog.h"

#include <QColorDialog>
#include <QFileDialog>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QSlider>
#include <QVBoxLayout>

SettingsDialog::SettingsDialog(const QColor& neonColor, int opacityPercent, QWidget* parent)
    : QDialog(parent),
      m_neonColor(neonColor),
      m_opacityPercent(opacityPercent),
      m_colorButton(new QPushButton(this)),
      m_opacitySlider(new QSlider(Qt::Horizontal, this)),
      m_backgroundButton(new QPushButton(tr("Arka Plan Seç"), this)) {
    setWindowTitle(tr("Neon Ayarları"));
    setModal(true);

    auto* layout = new QVBoxLayout(this);

    auto* neonRow = new QHBoxLayout();
    neonRow->addWidget(new QLabel(tr("Neon Rengi:"), this));
    updatePreviewButton();
    connect(m_colorButton, &QPushButton::clicked, this, &SettingsDialog::pickNeonColor);
    neonRow->addWidget(m_colorButton);

    auto* opacityRow = new QHBoxLayout();
    opacityRow->addWidget(new QLabel(tr("Saydamlık (%):"), this));
    m_opacitySlider->setRange(10, 100);
    m_opacitySlider->setValue(m_opacityPercent);
    opacityRow->addWidget(m_opacitySlider);

    connect(m_backgroundButton, &QPushButton::clicked, this, &SettingsDialog::pickBackgroundImage);

    auto* buttonRow = new QHBoxLayout();
    auto* okButton = new QPushButton(tr("Kaydet"), this);
    auto* cancelButton = new QPushButton(tr("İptal"), this);
    connect(okButton, &QPushButton::clicked, this, &SettingsDialog::accept);
    connect(cancelButton, &QPushButton::clicked, this, &SettingsDialog::reject);
    buttonRow->addStretch();
    buttonRow->addWidget(okButton);
    buttonRow->addWidget(cancelButton);

    layout->addLayout(neonRow);
    layout->addLayout(opacityRow);
    layout->addWidget(m_backgroundButton);
    layout->addLayout(buttonRow);
}

QColor SettingsDialog::selectedNeonColor() const {
    return m_neonColor;
}

int SettingsDialog::selectedOpacityPercent() const {
    return m_opacitySlider->value();
}

QString SettingsDialog::selectedBackgroundImage() const {
    return m_backgroundImage;
}

void SettingsDialog::pickNeonColor() {
    const QColor picked = QColorDialog::getColor(m_neonColor, this, tr("Neon Rengi Seç"));
    if (picked.isValid()) {
        m_neonColor = picked;
        updatePreviewButton();
    }
}

void SettingsDialog::pickBackgroundImage() {
    const QString file = QFileDialog::getOpenFileName(
        this,
        tr("Arka Plan Görseli Seç"),
        QString(),
        tr("Images (*.png *.jpg *.jpeg *.bmp *.webp)"));

    if (!file.isEmpty()) {
        m_backgroundImage = file;
        m_backgroundButton->setText(tr("Arka Plan: %1").arg(file));
    }
}

void SettingsDialog::updatePreviewButton() {
    m_colorButton->setText(m_neonColor.name());
    m_colorButton->setStyleSheet(QString("background-color: %1; color: black;").arg(m_neonColor.name()));
}
