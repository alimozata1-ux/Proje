#include "audio.h"
#include "console.h"

void audio_system_init(void) {
    console_puts("[SYS] Audio system initialized\n");
}

void audio_beep(unsigned freq_hz, unsigned duration_ms) {
    (void)freq_hz;
    (void)duration_ms;
    console_puts("[SYS] Beep requested\n");
}
