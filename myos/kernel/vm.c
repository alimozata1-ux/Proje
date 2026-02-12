#include "vm.h"
#include "string.h"
#include "vga.h"

#define VM_MEM 256
#define VM_REGS 4
#define VM_STACK 16

#define OP_HALT 0x00
#define OP_LOADI 0x10
#define OP_ADD 0x20
#define OP_PRINT 0x30
#define OP_JNZ 0x40

static unsigned char mem[VM_MEM];
static int regs[VM_REGS];
static int pc = 0;
static int halted = 0;
static int stack[VM_STACK];
static int sp = -1;

static unsigned char fetch(void) {
    if (pc < 0 || pc >= VM_MEM) {
        halted = 1;
        return OP_HALT;
    }
    return mem[pc++];
}

void vm_reset(void) {
    int i;
    for (i = 0; i < VM_MEM; i++) mem[i] = 0;
    for (i = 0; i < VM_REGS; i++) regs[i] = 0;
    for (i = 0; i < VM_STACK; i++) stack[i] = 0;
    pc = 0;
    sp = -1;
    halted = 0;
}

void vm_load_demo_program(void) {
    /* r0=5, r1=3, r2=r0+r1, print r2, halt */
    mem[0] = OP_LOADI; mem[1] = 0; mem[2] = 5;
    mem[3] = OP_LOADI; mem[4] = 1; mem[5] = 3;
    mem[6] = OP_ADD;   mem[7] = 2; mem[8] = 0; mem[9] = 1;
    mem[10] = OP_PRINT; mem[11] = 2;
    mem[12] = OP_HALT;
}

void vm_print_state(void) {
    char b[16];
    vga_write_string("[vm] pc=");
    kitoa(pc, b);
    vga_write_string(b);
    vga_write_string(" r0=");
    kitoa(regs[0], b);
    vga_write_string(b);
    vga_write_string(" r1=");
    kitoa(regs[1], b);
    vga_write_string(b);
    vga_write_string(" r2=");
    kitoa(regs[2], b);
    vga_write_string(b);
    vga_write_string(" r3=");
    kitoa(regs[3], b);
    vga_write_string(b);
    vga_write_string("\n");
}

void vm_run(void) {
    int steps = 0;
    char b[16];

    while (!halted && steps < 128) {
        unsigned char op = fetch();

        if (op == OP_HALT) {
            halted = 1;
        } else if (op == OP_LOADI) {
            int r = fetch();
            int v = (signed char)fetch();
            if (r >= 0 && r < VM_REGS) regs[r] = v;
        } else if (op == OP_ADD) {
            int d = fetch();
            int a = fetch();
            int c = fetch();
            if (d >= 0 && d < VM_REGS && a >= 0 && a < VM_REGS && c >= 0 && c < VM_REGS) {
                regs[d] = regs[a] + regs[c];
            }
        } else if (op == OP_PRINT) {
            int r = fetch();
            if (r >= 0 && r < VM_REGS) {
                vga_write_string("[vm] print r");
                kitoa(r, b);
                vga_write_string(b);
                vga_write_string("=");
                kitoa(regs[r], b);
                vga_write_string(b);
                vga_write_string("\n");
            }
        } else if (op == OP_JNZ) {
            int r = fetch();
            int addr = fetch();
            if (r >= 0 && r < VM_REGS && regs[r] != 0 && addr >= 0 && addr < VM_MEM) {
                pc = addr;
            }
        } else {
            vga_write_string("[vm] unknown opcode\n");
            halted = 1;
        }

        steps++;
    }

    if (steps >= 128) {
        vga_write_string("[vm] step limit reached\n");
    }

    vm_print_state();
}
