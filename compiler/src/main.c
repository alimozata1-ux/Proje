#include "../include/konec.h"
#include <stdio.h>

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input.kc> <output.mars32|output.mars64>\n", argv[0]);
        return 1;
    }
    return konec_compile_file(argv[1], argv[2]);
}
