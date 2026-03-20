#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { OP_PUSH = 1, OP_ADD = 2, OP_PRINT = 3, OP_HALT = 255 };

typedef struct {
    unsigned char *ram;
    size_t ram_size;
    unsigned char framebuffer[320 * 200];
    unsigned char disk[1024 * 128];
    int debug;
} kone_vm_t;

static unsigned read_u32(const unsigned char *p) {
    return (unsigned)p[0] | ((unsigned)p[1] << 8) | ((unsigned)p[2] << 16) | ((unsigned)p[3] << 24);
}

static void vm_log(kone_vm_t *vm, const char *msg) {
    if (vm->debug) {
        printf("[KONE VM][debug] %s\n", msg);
    }
}

static int run_program(kone_vm_t *vm, const unsigned char *buf, size_t sz) {
    int stack[256];
    int sp = -1;
    size_t ip = 2;

    while (ip < sz) {
        unsigned char op = buf[ip++];
        switch (op) {
            case OP_PUSH: {
                if (ip + 4 > sz) goto fail;
                stack[++sp] = (int)read_u32(&buf[ip]);
                ip += 4;
                vm_log(vm, "OP_PUSH");
                break;
            }
            case OP_ADD: {
                if (sp < 1) goto fail;
                stack[sp - 1] = stack[sp - 1] + stack[sp];
                sp--;
                vm_log(vm, "OP_ADD");
                break;
            }
            case OP_PRINT: {
                if (sp < 0) goto fail;
                printf("[KONE VM] %d\n", stack[sp--]);
                vm_log(vm, "OP_PRINT");
                break;
            }
            case OP_HALT:
                vm_log(vm, "OP_HALT");
                return 0;
            default:
                goto fail;
        }
    }

fail:
    fprintf(stderr, "runtime error\n");
    return 3;
}

int main(int argc, char **argv) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "Usage: %s <program.mars32|program.mars64> [--debug]\n", argv[0]);
        return 1;
    }

    kone_vm_t vm;
    memset(&vm, 0, sizeof(vm));
    vm.ram_size = 1024 * 1024;
    vm.ram = (unsigned char *)malloc(vm.ram_size);
    if (!vm.ram) {
        fprintf(stderr, "failed to allocate vm ram\n");
        return 1;
    }

    if (argc == 3 && strcmp(argv[2], "--debug") == 0) {
        vm.debug = 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("open");
        free(vm.ram);
        return 1;
    }

    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);

    unsigned char *buf = (unsigned char *)malloc((size_t)sz);
    if (!buf) {
        fclose(f);
        free(vm.ram);
        return 1;
    }

    if (fread(buf, 1, (size_t)sz, f) != (size_t)sz) {
        fprintf(stderr, "read error\n");
        fclose(f);
        free(buf);
        free(vm.ram);
        return 1;
    }
    fclose(f);

    if (sz < 2 || buf[0] != 'M' || (buf[1] != '3' && buf[1] != '6')) {
        fprintf(stderr, "invalid mars executable\n");
        free(buf);
        free(vm.ram);
        return 2;
    }

    int rc = run_program(&vm, buf, (size_t)sz);
    free(buf);
    free(vm.ram);
    return rc;
}
