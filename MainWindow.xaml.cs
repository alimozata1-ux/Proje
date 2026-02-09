using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;

namespace Proje;

public partial class MainWindow : Window
{
    private const string HomeUrl = "https://www.bing.com";
    private readonly ObservableCollection<BrowserTab> _tabs = [];
    private readonly List<string> _favorites = [];
    private readonly List<HistoryEntry> _history = [];
    private bool _isDarkTheme = true;

    private string DataFolder => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ModernBrowserWpf");
    private string FavoritesFile => Path.Combine(DataFolder, "favorites.json");
    private string HistoryFile => Path.Combine(DataFolder, "history.json");

    public MainWindow()
    {
        InitializeComponent();
        LoadPersistedData();
        AddNewTab(HomeUrl);
    }

    private BrowserTab? ActiveTab => TabsHeader.SelectedItem as BrowserTab;

    private async void AddNewTab(string initialUrl)
    {
        // Her sekme için bağımsız bir WebView2 instance oluşturulur.
        var webView = new WebView2();
        await webView.EnsureCoreWebView2Async();

        var tab = new BrowserTab
        {
            Header = "Yeni Sekme",
            WebView = webView
        };

        webView.NavigationStarting += (_, _) => LoadingBar.Visibility = Visibility.Visible;
        webView.NavigationCompleted += (_, args) =>
        {
            LoadingBar.Visibility = Visibility.Collapsed;
            if (args.IsSuccess)
            {
                var url = webView.Source?.ToString() ?? string.Empty;
                tab.Header = webView.CoreWebView2.DocumentTitle is { Length: > 0 } title ? title : url;
                AddressBar.Text = url;
                AddToHistory(url);
                TabsHeader.Items.Refresh();
            }
        };

        webView.CoreWebView2.HistoryChanged += (_, _) => UpdateNavButtons();
        webView.CoreWebView2.DocumentTitleChanged += (_, _) =>
        {
            tab.Header = webView.CoreWebView2.DocumentTitle;
            TabsHeader.Items.Refresh();
        };

        _tabs.Add(tab);
        TabsHeader.ItemsSource = _tabs;
        TabsHeader.ItemTemplate = CreateTabHeaderTemplate();
        TabsHeader.SelectedItem = tab;

        NavigateTo(initialUrl);
    }

    private DataTemplate CreateTabHeaderTemplate()
    {
        var template = new DataTemplate(typeof(BrowserTab));
        var spFactory = new FrameworkElementFactory(typeof(StackPanel));
        spFactory.SetValue(StackPanel.OrientationProperty, Orientation.Horizontal);

        var titleFactory = new FrameworkElementFactory(typeof(TextBlock));
        titleFactory.SetBinding(TextBlock.TextProperty, new System.Windows.Data.Binding(nameof(BrowserTab.Header)));
        titleFactory.SetValue(TextBlock.MarginProperty, new Thickness(0, 0, 8, 0));
        titleFactory.SetValue(TextBlock.ForegroundProperty, Brushes.WhiteSmoke);
        spFactory.AppendChild(titleFactory);

        var closeButtonFactory = new FrameworkElementFactory(typeof(Button));
        closeButtonFactory.SetValue(Button.ContentProperty, "×");
        closeButtonFactory.SetValue(Button.WidthProperty, 22.0);
        closeButtonFactory.SetValue(Button.HeightProperty, 22.0);
        closeButtonFactory.SetValue(Button.BackgroundProperty, Brushes.Transparent);
        closeButtonFactory.SetValue(Button.ForegroundProperty, Brushes.WhiteSmoke);
        closeButtonFactory.SetValue(Button.BorderThicknessProperty, new Thickness(0));
        closeButtonFactory.SetBinding(Button.TagProperty, new System.Windows.Data.Binding());
        closeButtonFactory.AddHandler(Button.ClickEvent, new RoutedEventHandler(CloseTabButton_Click));

        spFactory.AppendChild(closeButtonFactory);
        template.VisualTree = spFactory;
        return template;
    }

    private void CloseTabButton_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button { Tag: BrowserTab tab })
        {
            return;
        }

        tab.WebView.Dispose();
        _tabs.Remove(tab);

        if (_tabs.Count == 0)
        {
            AddNewTab(HomeUrl);
            return;
        }

        TabsHeader.SelectedIndex = Math.Max(0, TabsHeader.SelectedIndex - 1);
    }

    private void TabsHeader_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (ActiveTab is null)
        {
            return;
        }

        BrowserHost.Children.Clear();
        BrowserHost.Children.Add(ActiveTab.WebView);
        AddressBar.Text = ActiveTab.WebView.Source?.ToString() ?? string.Empty;
        UpdateNavButtons();
    }

    private void NavigateTo(string input)
    {
        if (ActiveTab?.WebView.CoreWebView2 is null)
        {
            return;
        }

        var target = NormalizeToUrl(input);
        AddressBar.Text = target;
        ActiveTab.WebView.CoreWebView2.Navigate(target);
    }

    private static string NormalizeToUrl(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
        {
            return HomeUrl;
        }

        if (Uri.TryCreate(input, UriKind.Absolute, out var uri) && !string.IsNullOrWhiteSpace(uri.Scheme))
        {
            return input;
        }

        return $"https://www.bing.com/search?q={Uri.EscapeDataString(input)}";
    }

    private void AddToHistory(string url)
    {
        if (string.IsNullOrWhiteSpace(url))
        {
            return;
        }

        _history.Insert(0, new HistoryEntry(url, DateTime.Now));
        if (_history.Count > 200)
        {
            _history.RemoveAt(_history.Count - 1);
        }

        PersistList(HistoryFile, _history);
    }

    private void LoadPersistedData()
    {
        Directory.CreateDirectory(DataFolder);

        if (File.Exists(FavoritesFile))
        {
            var list = JsonSerializer.Deserialize<List<string>>(File.ReadAllText(FavoritesFile));
            if (list is not null)
            {
                _favorites.AddRange(list);
            }
        }

        if (File.Exists(HistoryFile))
        {
            var list = JsonSerializer.Deserialize<List<HistoryEntry>>(File.ReadAllText(HistoryFile));
            if (list is not null)
            {
                _history.AddRange(list);
            }
        }
    }

    private static void PersistList<T>(string file, List<T> list)
    {
        File.WriteAllText(file, JsonSerializer.Serialize(list, new JsonSerializerOptions { WriteIndented = true }));
    }

    private void UpdateNavButtons()
    {
        // İstenirse butonların IsEnabled durumları burada yönetilebilir.
    }

    private void AddTabButton_Click(object sender, RoutedEventArgs e) => AddNewTab(HomeUrl);

    private void GoButton_Click(object sender, RoutedEventArgs e) => NavigateTo(AddressBar.Text);

    private void AddressBar_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter)
        {
            NavigateTo(AddressBar.Text);
        }
    }

    private void BackButton_Click(object sender, RoutedEventArgs e)
    {
        if (ActiveTab?.WebView.CoreWebView2?.CanGoBack == true)
        {
            ActiveTab.WebView.CoreWebView2.GoBack();
        }
    }

    private void ForwardButton_Click(object sender, RoutedEventArgs e)
    {
        if (ActiveTab?.WebView.CoreWebView2?.CanGoForward == true)
        {
            ActiveTab.WebView.CoreWebView2.GoForward();
        }
    }

    private void RefreshButton_Click(object sender, RoutedEventArgs e) => ActiveTab?.WebView.Reload();

    private void HomeButton_Click(object sender, RoutedEventArgs e) => NavigateTo(HomeUrl);

    private void AddFavoriteButton_Click(object sender, RoutedEventArgs e)
    {
        var url = AddressBar.Text;
        if (string.IsNullOrWhiteSpace(url) || _favorites.Contains(url))
        {
            return;
        }

        _favorites.Add(url);
        PersistList(FavoritesFile, _favorites);
    }

    private void ShowFavoritesButton_Click(object sender, RoutedEventArgs e)
    {
        var menu = new ContextMenu();

        if (_favorites.Count == 0)
        {
            menu.Items.Add(new MenuItem { Header = "Favori yok" });
        }

        foreach (var favorite in _favorites)
        {
            var item = new MenuItem { Header = favorite };
            item.Click += (_, _) => NavigateTo(favorite);
            menu.Items.Add(item);
        }

        menu.IsOpen = true;
    }

    private void ShowHistoryButton_Click(object sender, RoutedEventArgs e)
    {
        var menu = new ContextMenu();

        if (_history.Count == 0)
        {
            menu.Items.Add(new MenuItem { Header = "Geçmiş boş" });
        }

        foreach (var entry in _history.Take(20))
        {
            var item = new MenuItem { Header = $"{entry.VisitedAt:g} - {entry.Url}" };
            item.Click += (_, _) => NavigateTo(entry.Url);
            menu.Items.Add(item);
        }

        menu.IsOpen = true;
    }

    private void ToggleThemeButton_Click(object sender, RoutedEventArgs e)
    {
        _isDarkTheme = !_isDarkTheme;

        Background = _isDarkTheme ? new SolidColorBrush((Color)ColorConverter.ConvertFromString("#0F172A")) : Brushes.WhiteSmoke;
        LoadingBar.Foreground = _isDarkTheme ? Brushes.DodgerBlue : Brushes.MediumVioletRed;
    }

    private void MinimizeButton_Click(object sender, RoutedEventArgs e) => WindowState = WindowState.Minimized;

    private void MaximizeButton_Click(object sender, RoutedEventArgs e)
        => WindowState = WindowState == WindowState.Maximized ? WindowState.Normal : WindowState.Maximized;

    private void CloseButton_Click(object sender, RoutedEventArgs e) => Close();

    private void TitleBar_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        if (e.ClickCount == 2)
        {
            MaximizeButton_Click(sender, e);
            return;
        }

        DragMove();
    }
}

public sealed class BrowserTab
{
    public string Header { get; set; } = "Yeni Sekme";
    public required WebView2 WebView { get; init; }
}

public sealed record HistoryEntry(string Url, DateTime VisitedAt);
