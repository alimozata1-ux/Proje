//go:build windows

package main

import (
	"encoding/json"
	"fmt"
	"image/color"
	"os"
	"path/filepath"
	"strings"

	"github.com/lxn/walk"
	. "github.com/lxn/walk/declarative"
)

type AppSettings struct {
	Homepage          string  `json:"homepage"`
	SearchEngine      string  `json:"search_engine"`
	ToolbarOpacity    float64 `json:"toolbar_opacity"`
	NeonColor         string  `json:"neon_color"`
	ShowStatusBar     bool    `json:"show_status_bar"`
	EnableJavaScript  bool    `json:"enable_javascript"`
	EnableDevMode     bool    `json:"enable_dev_mode"`
	OpenLastPageOnRun bool    `json:"open_last_page_on_run"`
	DownloadFolder    string  `json:"download_folder"`
	ZoomPercent       int     `json:"zoom_percent"`
}

func defaultSettings() AppSettings {
	home, _ := os.UserHomeDir()
	return AppSettings{
		Homepage:          "https://duckduckgo.com",
		SearchEngine:      "https://duckduckgo.com/?q=%s",
		ToolbarOpacity:    0.75,
		NeonColor:         "#00F5FF",
		ShowStatusBar:     true,
		EnableJavaScript:  true,
		EnableDevMode:     false,
		OpenLastPageOnRun: true,
		DownloadFolder:    filepath.Join(home, "Downloads"),
		ZoomPercent:       100,
	}
}

func settingsPath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return "neon-browser-settings.json"
	}
	return filepath.Join(home, ".neon-browser-settings.json")
}

func loadSettings() AppSettings {
	cfg := defaultSettings()
	data, err := os.ReadFile(settingsPath())
	if err != nil {
		return cfg
	}
	_ = json.Unmarshal(data, &cfg)
	return cfg
}

func saveSettings(cfg AppSettings) error {
	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(settingsPath(), data, 0o644)
}

func parseHexColor(hex string) color.Color {
	hex = strings.TrimPrefix(strings.TrimSpace(hex), "#")
	if len(hex) != 6 {
		return walk.RGB(0, 245, 255)
	}
	var r, g, b uint8
	_, err := fmt.Sscanf(hex, "%02x%02x%02x", &r, &g, &b)
	if err != nil {
		_, _ = fmt.Sscanf(strings.ToUpper(hex), "%02X%02X%02X", &r, &g, &b)
	}
	return walk.RGB(r, g, b)
}

func ensureURLOrSearch(input, searchPattern string) string {
	input = strings.TrimSpace(input)
	if input == "" {
		return "https://duckduckgo.com"
	}
	if strings.HasPrefix(input, "http://") || strings.HasPrefix(input, "https://") {
		return input
	}
	if strings.Contains(input, ".") && !strings.Contains(input, " ") {
		return "https://" + input
	}
	query := strings.ReplaceAll(input, " ", "+")
	return fmt.Sprintf(searchPattern, query)
}

func applyToolbarStyle(container *walk.Composite, neonLine *walk.Label, cfg AppSettings) {
	alpha := uint8(cfg.ToolbarOpacity * 255)
	bg, _ := walk.NewSolidColorBrush(walk.RGBA(10, 12, 24, alpha))
	container.SetBackground(bg)

	lineBrush, _ := walk.NewSolidColorBrush(parseHexColor(cfg.NeonColor))
	neonLine.SetBackground(lineBrush)
}

func openSettingsDialog(owner walk.Form, cfg *AppSettings, applyUI func()) {
	var dlg *walk.Dialog
	var acceptPB, cancelPB *walk.PushButton
	var homepageLE, searchLE, neonLE, downloadLE *walk.LineEdit
	var opacitySB, zoomSB *walk.Slider
	var statusCB, jsCB, devCB, restoreCB *walk.CheckBox

	tmp := *cfg

	_ = Dialog{
		AssignTo:      &dlg,
		Title:         "Detaylı Ayarlar",
		MinSize:       Size{Width: 520, Height: 430},
		DefaultButton: &acceptPB,
		CancelButton:  &cancelPB,
		Layout:        VBox{Margins: Margins{Left: 14, Top: 12, Right: 14, Bottom: 12}, Spacing: 8},
		Children: []Widget{
			Label{Text: "Ana sayfa URL"},
			LineEdit{AssignTo: &homepageLE, Text: tmp.Homepage},
			Label{Text: "Arama motoru deseni (%s sorgu için)"},
			LineEdit{AssignTo: &searchLE, Text: tmp.SearchEngine},
			Label{Text: "Araç çubuğu şeffaflığı (0-100)"},
			Slider{AssignTo: &opacitySB, MinValue: 0, MaxValue: 100, Value: int(tmp.ToolbarOpacity * 100)},
			Label{Text: "Neon çizgi rengi (Hex - ör: #00F5FF)"},
			LineEdit{AssignTo: &neonLE, Text: tmp.NeonColor},
			Label{Text: "Yakınlaştırma (%)"},
			Slider{AssignTo: &zoomSB, MinValue: 50, MaxValue: 300, Value: tmp.ZoomPercent},
			CheckBox{AssignTo: &statusCB, Text: "Durum çubuğunu göster", Checked: tmp.ShowStatusBar},
			CheckBox{AssignTo: &jsCB, Text: "JavaScript etkin (WebView varsayılanı)", Checked: tmp.EnableJavaScript},
			CheckBox{AssignTo: &devCB, Text: "Geliştirici modu", Checked: tmp.EnableDevMode},
			CheckBox{AssignTo: &restoreCB, Text: "Son sayfayı aç", Checked: tmp.OpenLastPageOnRun},
			Label{Text: "İndirme klasörü"},
			LineEdit{AssignTo: &downloadLE, Text: tmp.DownloadFolder},
			Composite{
				Layout: HBox{Spacing: 8},
				Children: []Widget{
					HSpacer{},
					PushButton{
						AssignTo: &acceptPB,
						Text:     "Kaydet",
						OnClicked: func() {
							tmp.Homepage = homepageLE.Text()
							tmp.SearchEngine = searchLE.Text()
							tmp.ToolbarOpacity = float64(opacitySB.Value()) / 100
							tmp.NeonColor = neonLE.Text()
							tmp.ZoomPercent = zoomSB.Value()
							tmp.ShowStatusBar = statusCB.Checked()
							tmp.EnableJavaScript = jsCB.Checked()
							tmp.EnableDevMode = devCB.Checked()
							tmp.OpenLastPageOnRun = restoreCB.Checked()
							tmp.DownloadFolder = downloadLE.Text()
							*cfg = tmp
							_ = saveSettings(*cfg)
							applyUI()
							dlg.Accept()
						},
					},
					PushButton{AssignTo: &cancelPB, Text: "İptal", OnClicked: func() { dlg.Cancel() }},
				},
			},
		},
	}.Run(owner)
}

func main() {
	cfg := loadSettings()

	var mw *walk.MainWindow
	var webView *walk.WebView
	var addressBar *walk.LineEdit
	var statusLabel *walk.Label
	var toolbarPanel *walk.Composite
	var neonLine *walk.Label

	currentURL := cfg.Homepage

	applyUI := func() {
		applyToolbarStyle(toolbarPanel, neonLine, cfg)
		if statusLabel != nil {
			statusLabel.SetVisible(cfg.ShowStatusBar)
		}
		if webView != nil {
			_ = webView.SetZoomFactor(float64(cfg.ZoomPercent) / 100)
		}
	}

	navigate := func() {
		url := ensureURLOrSearch(addressBar.Text(), cfg.SearchEngine)
		_ = webView.SetURL(url)
	}

	_ = MainWindow{
		AssignTo: &mw,
		Title:    "Neon Browser (Go)",
		MinSize:  Size{Width: 1280, Height: 820},
		Layout:   VBox{Margins: Margins{Left: 0, Top: 0, Right: 0, Bottom: 0}, Spacing: 0},
		Children: []Widget{
			Composite{
				AssignTo: &toolbarPanel,
				Layout:   VBox{Margins: Margins{Left: 10, Top: 8, Right: 10, Bottom: 4}, Spacing: 5},
				Children: []Widget{
					Composite{
						Layout: HBox{Spacing: 6},
						Children: []Widget{
							PushButton{Text: "◀", OnClicked: func() { webView.GoBack() }},
							PushButton{Text: "▶", OnClicked: func() { webView.GoForward() }},
							PushButton{Text: "⟳", OnClicked: func() { webView.Reload() }},
							LineEdit{AssignTo: &addressBar, Text: cfg.Homepage, OnKeyDown: func(key walk.Key) {
								if key == walk.KeyReturn {
									navigate()
								}
							}},
							PushButton{Text: "Git", OnClicked: navigate},
							PushButton{Text: "Ayarlar", OnClicked: func() { openSettingsDialog(mw, &cfg, applyUI) }},
						},
					},
					Label{AssignTo: &neonLine, MinSize: Size{Height: 3}},
				},
			},
			WebView{
				AssignTo: &webView,
				URL:      cfg.Homepage,
				OnURLChanged: func() {
					currentURL = webView.URL()
					addressBar.SetText(currentURL)
					if statusLabel != nil {
						statusLabel.SetText("Aktif: " + currentURL)
					}
				},
			},
			Label{AssignTo: &statusLabel, Text: "Hazır", MinSize: Size{Height: 24}},
		},
		OnBoundsChanged: func() {
			if cfg.OpenLastPageOnRun {
				_ = os.WriteFile("last_url.txt", []byte(currentURL), 0o644)
			}
		},
	}.Create()

	if cfg.OpenLastPageOnRun {
		if last, err := os.ReadFile("last_url.txt"); err == nil && strings.TrimSpace(string(last)) != "" {
			currentURL = strings.TrimSpace(string(last))
			addressBar.SetText(currentURL)
			_ = webView.SetURL(currentURL)
		}
	}

	applyUI()
	mw.Run()
}
