#include "browser.h"
#include "string.h"
#include "vga.h"

typedef struct {
    const char* url;
    const char* html;
} browser_page_t;

typedef struct {
    int used;
    int id;
    char url[BROWSER_URL_MAX];
    char history[BROWSER_MAX_HISTORY][BROWSER_URL_MAX];
    int history_count;
    int history_index;
} browser_tab_t;

static browser_tab_t tabs[BROWSER_MAX_TABS];
static int next_tab_id = 1;
static int current_tab = -1;

static char bookmarks[16][BROWSER_URL_MAX];
static int bookmark_count = 0;

static const browser_page_t pages[] = {
    {"http://home", "<html><title>MyOS Browser</title><body><h1>MyOS Home</h1><p>Welcome to text browser.</p><p>Try: http://news, http://docs, http://superx323</p></body></html>"},
    {"http://news", "<html><body><h1>News</h1><p>Kernel upgraded with taskbar, windowing and icons.</p><p>Now browsing in text mode.</p></body></html>"},
    {"http://docs", "<html><body><h1>Docs</h1><p>Commands: browser open URL</p><p>browser back | browser forward | browser tabs</p></body></html>"},
    {"http://superx323", "<html><body><h1>superx323</h1><p>Executable profile page loaded from built-in content.</p></body></html>"}
};

static void print_number(int value) {
    char buf[16];
    kitoa(value, buf);
    vga_write_string(buf);
}

static int str_eq(const char* a, const char* b) {
    return kstrcmp(a, b) == 0;
}

static void copy_text(char* dst, const char* src, int cap) {
    int i = 0;
    if (cap <= 0) {
        return;
    }
    while (src[i] && i < cap - 1) {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
}

static const char* find_html(const char* url) {
    int i;
    for (i = 0; i < (int)(sizeof(pages) / sizeof(pages[0])); i++) {
        if (str_eq(url, pages[i].url)) {
            return pages[i].html;
        }
    }
    return "<html><body><h1>404</h1><p>Page not found.</p></body></html>";
}

static void render_html_text(const char* html) {
    int in_tag = 0;
    while (*html) {
        char c = *html++;
        if (c == '<') {
            in_tag = 1;
            continue;
        }
        if (c == '>') {
            in_tag = 0;
            continue;
        }
        if (!in_tag) {
            vga_put_char(c);
        }
    }
    vga_write_string("\n");
}

static int alloc_tab(void) {
    int i;
    for (i = 0; i < BROWSER_MAX_TABS; i++) {
        if (!tabs[i].used) {
            tabs[i].used = 1;
            tabs[i].id = next_tab_id++;
            tabs[i].url[0] = '\0';
            tabs[i].history_count = 0;
            tabs[i].history_index = -1;
            return i;
        }
    }
    return -1;
}

static void push_history(browser_tab_t* tab, const char* url) {
    int i;

    if (tab->history_index < tab->history_count - 1) {
        tab->history_count = tab->history_index + 1;
    }

    if (tab->history_count < BROWSER_MAX_HISTORY) {
        copy_text(tab->history[tab->history_count], url, BROWSER_URL_MAX);
        tab->history_count++;
        tab->history_index = tab->history_count - 1;
        return;
    }

    for (i = 1; i < BROWSER_MAX_HISTORY; i++) {
        copy_text(tab->history[i - 1], tab->history[i], BROWSER_URL_MAX);
    }
    copy_text(tab->history[BROWSER_MAX_HISTORY - 1], url, BROWSER_URL_MAX);
    tab->history_count = BROWSER_MAX_HISTORY;
    tab->history_index = BROWSER_MAX_HISTORY - 1;
}

static browser_tab_t* current(void) {
    if (current_tab < 0 || current_tab >= BROWSER_MAX_TABS || !tabs[current_tab].used) {
        return (browser_tab_t*)0;
    }
    return &tabs[current_tab];
}

static void browser_render_current(void) {
    browser_tab_t* tab = current();
    const char* html;
    if (!tab) {
        vga_write_string("browser: no active tab\n");
        return;
    }

    vga_write_string("\n[BROWSER] tab ");
    print_number(tab->id);
    vga_write_string(" url=");
    vga_write_string(tab->url);
    vga_write_string("\n");

    html = find_html(tab->url);
    render_html_text(html);
}

void browser_init(void) {
    int i;
    for (i = 0; i < BROWSER_MAX_TABS; i++) {
        tabs[i].used = 0;
    }
    bookmark_count = 0;

    current_tab = alloc_tab();
    if (current_tab >= 0) {
        copy_text(tabs[current_tab].url, "http://home", BROWSER_URL_MAX);
        push_history(&tabs[current_tab], tabs[current_tab].url);
    }
}

void browser_home(void) {
    browser_open("http://home");
}

void browser_open(const char* url) {
    browser_tab_t* tab = current();
    if (!tab) {
        int idx = alloc_tab();
        if (idx < 0) {
            vga_write_string("browser: cannot allocate tab\n");
            return;
        }
        current_tab = idx;
        tab = &tabs[current_tab];
    }

    copy_text(tab->url, url, BROWSER_URL_MAX);
    push_history(tab, tab->url);
    browser_render_current();
}

void browser_back(void) {
    browser_tab_t* tab = current();
    if (!tab || tab->history_index <= 0) {
        vga_write_string("browser: no back history\n");
        return;
    }
    tab->history_index--;
    copy_text(tab->url, tab->history[tab->history_index], BROWSER_URL_MAX);
    browser_render_current();
}

void browser_forward(void) {
    browser_tab_t* tab = current();
    if (!tab || tab->history_index >= tab->history_count - 1) {
        vga_write_string("browser: no forward history\n");
        return;
    }
    tab->history_index++;
    copy_text(tab->url, tab->history[tab->history_index], BROWSER_URL_MAX);
    browser_render_current();
}

void browser_tabs(void) {
    int i;
    int found = 0;
    vga_write_string("browser tabs:\n");
    for (i = 0; i < BROWSER_MAX_TABS; i++) {
        if (!tabs[i].used) {
            continue;
        }
        found = 1;
        vga_write_string("  id=");
        print_number(tabs[i].id);
        if (i == current_tab) {
            vga_write_string(" *");
        }
        vga_write_string(" url=");
        vga_write_string(tabs[i].url);
        vga_write_string("\n");
    }
    if (!found) {
        vga_write_string("  (no tabs)\n");
    }
}

void browser_switch(int tab_id) {
    int i;
    for (i = 0; i < BROWSER_MAX_TABS; i++) {
        if (tabs[i].used && tabs[i].id == tab_id) {
            current_tab = i;
            browser_render_current();
            return;
        }
    }
    vga_write_string("browser: tab not found\n");
}

void browser_close(int tab_id) {
    int i;
    for (i = 0; i < BROWSER_MAX_TABS; i++) {
        if (tabs[i].used && tabs[i].id == tab_id) {
            tabs[i].used = 0;
            if (current_tab == i) {
                current_tab = -1;
                for (i = 0; i < BROWSER_MAX_TABS; i++) {
                    if (tabs[i].used) {
                        current_tab = i;
                        break;
                    }
                }
            }
            vga_write_string("browser: tab closed\n");
            return;
        }
    }
    vga_write_string("browser: tab not found\n");
}

void browser_bookmark_add(const char* url) {
    if (bookmark_count >= 16) {
        vga_write_string("browser: bookmarks full\n");
        return;
    }
    copy_text(bookmarks[bookmark_count++], url, BROWSER_URL_MAX);
    vga_write_string("browser: bookmark added\n");
}

void browser_bookmarks(void) {
    int i;
    vga_write_string("browser bookmarks:\n");
    for (i = 0; i < bookmark_count; i++) {
        vga_write_string("  ");
        vga_write_string(bookmarks[i]);
        vga_write_string("\n");
    }
    if (bookmark_count == 0) {
        vga_write_string("  (none)\n");
    }
}
