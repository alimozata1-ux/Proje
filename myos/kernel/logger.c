#include "logger.h"
#include "serial.h"
#include "vga.h"

static void log_prefix(const char* level, const char* tag) {
    vga_write_string("[");
    vga_write_string(level);
    vga_write_string("] ");
    vga_write_string(tag);
    vga_write_string(": ");

    serial_write("[");
    serial_write(level);
    serial_write("] ");
    serial_write(tag);
    serial_write(": ");
}

static void log_line(const char* msg) {
    vga_write_string(msg);
    vga_write_string("\n");
    serial_write(msg);
    serial_write("\n");
}

void log_info(const char* tag, const char* message) {
    log_prefix("INFO", tag);
    log_line(message);
}

void log_warn(const char* tag, const char* message) {
    log_prefix("WARN", tag);
    log_line(message);
}

void log_error(const char* tag, const char* message) {
    log_prefix("ERR", tag);
    log_line(message);
}

void log_hex(const char* tag, const char* key, unsigned int value) {
    log_prefix("HEX", tag);
    vga_write_string(key);
    vga_write_string(" = ");

    serial_write(key);
    serial_write(" = ");
    serial_write_hex(value);
    serial_write("\n");
}
