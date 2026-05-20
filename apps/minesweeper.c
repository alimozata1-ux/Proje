#include "../kernel/gui/window.h"
#include "../kernel/graphics.h"
#include <stdint.h>
typedef struct{uint8_t is_mine,is_revealed,is_flagged,neighbor_mines;} Cell;
static Window*win; static Cell b[8][8]; static uint8_t over=0,won=0;
static void initg(void){ for(int y=0;y<8;y++)for(int x=0;x<8;x++){ b[y][x].is_mine=((x*y+x+3)%11==0); b[y][x].is_revealed=0; b[y][x].is_flagged=0; } for(int y=0;y<8;y++)for(int x=0;x<8;x++){ int n=0; for(int j=-1;j<=1;j++)for(int i=-1;i<=1;i++){int nx=x+i,ny=y+j; if(nx>=0&&ny>=0&&nx<8&&ny<8&&b[ny][nx].is_mine)n++;} b[y][x].neighbor_mines=n; }}
void mines_open(void){ win=window_create("Mayin Tarlasi",420,120,220,260,1); over=won=0; initg(); }
void mines_draw(void){ if(!win)return; for(int y=0;y<8;y++)for(int x=0;x<8;x++){ int px=win->x+20+x*22,py=win->y+40+y*22; uint32_t c=b[y][x].is_revealed?0x00ECE9D8:0x00A0A0A0; if(b[y][x].is_flagged)c=0x000053E2; if(over&&b[y][x].is_mine)c=0x00D32F2F; draw_rect(px,py,20,20,c);} }
void mines_left(int mx,int my){ if(!win||over)return; int x=(mx-(win->x+20))/22,y=(my-(win->y+40))/22; if(x<0||y<0||x>=8||y>=8)return; b[y][x].is_revealed=1; if(b[y][x].is_mine) over=1; }
void mines_right(int mx,int my){ if(!win||over)return; int x=(mx-(win->x+20))/22,y=(my-(win->y+40))/22; if(x<0||y<0||x>=8||y>=8)return; b[y][x].is_flagged=!b[y][x].is_flagged; }
