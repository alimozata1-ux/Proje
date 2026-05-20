#ifndef APP_LAUNCHER_H
#define APP_LAUNCHER_H
void launch_notepad(void); void launch_calc(void); void launch_image_viewer(void); void launch_minesweeper(void); void launch_browser(void); void launch_terminal(void); void launch_settings(void); void launch_ledger(void); void launch_control_panel(void);
void apps_render(void); void apps_on_left_click(int mx,int my); void apps_on_right_click(int mx,int my); void apps_on_key(char c);
#endif
