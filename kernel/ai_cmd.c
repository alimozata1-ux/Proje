#include "ai_cmd.h"
#include "console.h"
#include "../lib/kone_string.h"

void ai_cmd_init(void) {
    console_puts("[SYS] AI command interpreter initialized\n");
}

int ai_cmd_execute(const char *cmd) {
    if (!cmd) return -1;

    if (k_strcmp(cmd, "open settings") == 0) {
        console_puts("[AI] Opening settings...\n");
        return 0;
    }
    if (k_strcmp(cmd, "open terminal") == 0) {
        console_puts("[AI] Opening terminal...\n");
        return 0;
    }
    console_puts("[AI] Unknown command\n");
    return 1;
}
