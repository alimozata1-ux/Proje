#include "../include/konec.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Basit AST: sadece print(NUM [+ NUM]) cümlesi. */
typedef struct {
    int lhs;
    int rhs;
    int has_add;
} ast_print_t;

static int expect(lexer_t *lx, token_kind_t kind, const char *msg) {
    if (lx->current.kind != kind) {
        fprintf(stderr, "parse error: %s\n", msg);
        return -1;
    }
    lexer_next(lx);
    return 0;
}

static int parse_print_stmt(lexer_t *lx, ast_print_t *out) {
    if (expect(lx, TOK_PRINT, "expected 'print'")) return -1;
    if (expect(lx, TOK_LPAREN, "expected '('") ) return -1;
    if (lx->current.kind != TOK_NUMBER) return -1;
    out->lhs = lx->current.number;
    lexer_next(lx);

    out->has_add = 0;
    out->rhs = 0;
    if (lx->current.kind == TOK_PLUS) {
        out->has_add = 1;
        lexer_next(lx);
        if (lx->current.kind != TOK_NUMBER) return -1;
        out->rhs = lx->current.number;
        lexer_next(lx);
    }

    if (expect(lx, TOK_RPAREN, "expected ')'")) return -1;
    if (expect(lx, TOK_SEMI, "expected ';'")) return -1;
    return 0;
}

/* Bytecode format:
 *  'M''3' or 'M''6'
 *  OP_PUSH imm32
 *  [OP_PUSH imm32 OP_ADD]
 *  OP_PRINT
 *  OP_HALT
 */
enum { OP_PUSH = 1, OP_ADD = 2, OP_PRINT = 3, OP_HALT = 255 };

static void emit_u32(FILE *f, unsigned v) {
    unsigned char b[4] = {
        (unsigned char)(v & 0xFF),
        (unsigned char)((v >> 8) & 0xFF),
        (unsigned char)((v >> 16) & 0xFF),
        (unsigned char)((v >> 24) & 0xFF)
    };
    fwrite(b, 1, 4, f);
}

int konec_compile_file(const char *input, const char *output) {
    FILE *fi = fopen(input, "rb");
    if (!fi) {
        perror("open input");
        return 1;
    }

    fseek(fi, 0, SEEK_END);
    long sz = ftell(fi);
    fseek(fi, 0, SEEK_SET);

    char *src = (char *)malloc((size_t)sz + 1);
    if (!src) return 1;
    if (fread(src, 1, (size_t)sz, fi) != (size_t)sz) {
        fprintf(stderr, "read error\n");
        fclose(fi);
        free(src);
        return 1;
    }
    fclose(fi);
    src[sz] = '\0';

    lexer_t lx;
    lexer_init(&lx, src);

    ast_print_t stmt;
    if (parse_print_stmt(&lx, &stmt)) {
        fprintf(stderr, "unsupported source or syntax\n");
        free(src);
        return 2;
    }

    FILE *fo = fopen(output, "wb");
    if (!fo) {
        perror("open output");
        free(src);
        return 1;
    }

    const char *ext = strrchr(output, '.');
    if (ext && strcmp(ext, ".mars64") == 0) {
        fputc('M', fo); fputc('6', fo);
    } else {
        fputc('M', fo); fputc('3', fo);
    }

    fputc(OP_PUSH, fo); emit_u32(fo, (unsigned)stmt.lhs);
    if (stmt.has_add) {
        fputc(OP_PUSH, fo); emit_u32(fo, (unsigned)stmt.rhs);
        fputc(OP_ADD, fo);
    }
    fputc(OP_PRINT, fo);
    fputc(OP_HALT, fo);

    fclose(fo);
    free(src);
    return 0;
}
