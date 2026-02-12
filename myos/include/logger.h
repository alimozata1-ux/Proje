#ifndef LOGGER_H
#define LOGGER_H

void log_info(const char* tag, const char* message);
void log_warn(const char* tag, const char* message);
void log_error(const char* tag, const char* message);
void log_hex(const char* tag, const char* key, unsigned int value);

#endif
