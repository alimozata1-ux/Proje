#include "../kernel/gui/window.h"
#include "../kernel/gui/widgets.h"
#include "../kernel/fs/fat.h"
#include "../kernel/graphics.h"
#include <stdint.h>
static Window*win; static Button*prevb,*nextb,*zin,*zout; static uint8_t img[65536]; static uint32_t img_sz;
void image_viewer_open(void){ win=window_create("Windows Resim Goruntuleyicisi",140,90,560,420,1); prevb=button_create(10,380,70,24,"Onceki",0); nextb=button_create(90,380,70,24,"Sonraki",0); zin=button_create(170,380,70,24,"Buyut",0); zout=button_create(250,380,70,24,"Kucult",0); (void)fat_read_file("BLISS.BMP",img,&img_sz); }
void image_viewer_draw(void){ if(!win)return; for(int y=0;y<220;y++) for(int x=0;x<320;x++){ uint32_t off=(y*320+x)*3; if(off+2<img_sz){ uint32_t c=(img[off])|(img[off+1]<<8)|(img[off+2]<<16); put_pixel(win->x+10+x,win->y+50+y,c);} } widget_draw_button(prevb,win->x,win->y); widget_draw_button(nextb,win->x,win->y); widget_draw_button(zin,win->x,win->y); widget_draw_button(zout,win->x,win->y);} 
void image_viewer_click(int mx,int my){(void)mx;(void)my;}
