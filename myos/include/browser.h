#ifndef BROWSER_H
#define BROWSER_H

#define BROWSER_MAX_TABS 6
#define BROWSER_MAX_HISTORY 16
#define BROWSER_URL_MAX 96

void browser_init(void);
void browser_home(void);
void browser_open(const char* url);
void browser_back(void);
void browser_forward(void);
void browser_tabs(void);
void browser_switch(int tab_id);
void browser_close(int tab_id);
void browser_bookmark_add(const char* url);
void browser_bookmarks(void);

#endif
