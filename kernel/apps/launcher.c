#include "launcher.h"
void notepad_open(void); void notepad_draw(void); void notepad_click(int,int); void notepad_key(char);
void calc_open(void); void calc_draw(void); void calc_click(int,int);
void image_viewer_open(void); void image_viewer_draw(void); void image_viewer_click(int,int);
void mines_open(void); void mines_draw(void); void mines_left(int,int); void mines_right(int,int);
void browser_open(void); void browser_draw(void); void browser_click(int,int); void browser_key(char);
void terminal_open(void); void terminal_draw(void); void terminal_click(int,int); void terminal_key(char);
void settings_open(void); void settings_draw(void); void settings_click(int,int); void settings_key(char);
void control_panel_open(void); void control_panel_draw(void); void control_panel_click(int,int); void control_panel_key(char);
void ledger_open(void); void ledger_draw(void); void ledger_click(int,int); void ledger_key(char);

void launch_notepad(void){ notepad_open(); }
void launch_calc(void){ calc_open(); }
void launch_image_viewer(void){ image_viewer_open(); }
void launch_minesweeper(void){ mines_open(); }
void launch_browser(void){ browser_open(); }
void launch_terminal(void){ terminal_open(); }
void launch_settings(void){ settings_open(); }
void launch_ledger(void){ ledger_open(); }
void launch_control_panel(void){ control_panel_open(); }

void apps_init(void){}
void apps_render(void){ notepad_draw(); calc_draw(); image_viewer_draw(); mines_draw(); browser_draw(); terminal_draw(); settings_draw(); ledger_draw(); control_panel_draw(); }
void apps_on_left_click(int mx,int my){ notepad_click(mx,my); calc_click(mx,my); image_viewer_click(mx,my); mines_left(mx,my); browser_click(mx,my); terminal_click(mx,my); settings_click(mx,my); ledger_click(mx,my); control_panel_click(mx,my); }
void apps_on_right_click(int mx,int my){ mines_right(mx,my); }
void apps_on_key(char c){ notepad_key(c); browser_key(c); terminal_key(c); settings_key(c); ledger_key(c); control_panel_key(c); }
