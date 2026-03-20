#ifndef KONEC_H
#define KONEC_H

#include <stddef.h>

typedef enum {
    TOK_EOF = 0,
    TOK_IDENT,
    TOK_NUMBER,
    TOK_FN,
    TOK_LET,
    TOK_IF,
    TOK_ELSE,
    TOK_WHILE,
    TOK_RETURN,
    TOK_PRINT,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_LBRACE,
    TOK_RBRACE,
    TOK_SEMI,
    TOK_ASSIGN,
    TOK_PLUS
} token_kind_t;

typedef struct {
    token_kind_t kind;
    char lexeme[64];
    int number;
} token_t;

typedef struct {
    const char *src;
    size_t pos;
    token_t current;
} lexer_t;

void lexer_init(lexer_t *lx, const char *src);
void lexer_next(lexer_t *lx);

int konec_compile_file(const char *input, const char *output);

#endif
