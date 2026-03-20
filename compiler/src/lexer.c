#include "../include/konec.h"
#include <ctype.h>
#include <string.h>

static int is_ident_start(int c) { return isalpha(c) || c == '_'; }
static int is_ident(int c) { return isalnum(c) || c == '_'; }

void lexer_init(lexer_t *lx, const char *src) {
    lx->src = src;
    lx->pos = 0;
    lexer_next(lx);
}

static void read_ident(lexer_t *lx) {
    size_t i = 0;
    while (is_ident(lx->src[lx->pos]) && i < sizeof(lx->current.lexeme) - 1) {
        lx->current.lexeme[i++] = lx->src[lx->pos++];
    }
    lx->current.lexeme[i] = '\0';

    if (!strcmp(lx->current.lexeme, "fn")) lx->current.kind = TOK_FN;
    else if (!strcmp(lx->current.lexeme, "let")) lx->current.kind = TOK_LET;
    else if (!strcmp(lx->current.lexeme, "if")) lx->current.kind = TOK_IF;
    else if (!strcmp(lx->current.lexeme, "else")) lx->current.kind = TOK_ELSE;
    else if (!strcmp(lx->current.lexeme, "while")) lx->current.kind = TOK_WHILE;
    else if (!strcmp(lx->current.lexeme, "return")) lx->current.kind = TOK_RETURN;
    else if (!strcmp(lx->current.lexeme, "print")) lx->current.kind = TOK_PRINT;
    else lx->current.kind = TOK_IDENT;
}

static void read_number(lexer_t *lx) {
    int val = 0;
    while (isdigit((unsigned char)lx->src[lx->pos])) {
        val = val * 10 + (lx->src[lx->pos++] - '0');
    }
    lx->current.kind = TOK_NUMBER;
    lx->current.number = val;
}

void lexer_next(lexer_t *lx) {
    while (isspace((unsigned char)lx->src[lx->pos])) lx->pos++;

    char c = lx->src[lx->pos];
    lx->current.lexeme[0] = '\0';
    lx->current.number = 0;

    if (!c) {
        lx->current.kind = TOK_EOF;
        return;
    }

    if (is_ident_start(c)) {
        read_ident(lx);
        return;
    }

    if (isdigit((unsigned char)c)) {
        read_number(lx);
        return;
    }

    lx->pos++;
    switch (c) {
        case '(': lx->current.kind = TOK_LPAREN; break;
        case ')': lx->current.kind = TOK_RPAREN; break;
        case '{': lx->current.kind = TOK_LBRACE; break;
        case '}': lx->current.kind = TOK_RBRACE; break;
        case ';': lx->current.kind = TOK_SEMI; break;
        case '=': lx->current.kind = TOK_ASSIGN; break;
        case '+': lx->current.kind = TOK_PLUS; break;
        default: lx->current.kind = TOK_EOF; break;
    }
}
