#ifndef PANIC_H
#define PANIC_H

void panic(const char* reason);
void panic_hex(const char* reason, unsigned int code);

#endif
