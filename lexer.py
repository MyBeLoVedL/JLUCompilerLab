#!/bin/python3

import header
from header import ASTnode, TokenType, show_error
from header import Token
from header import bcolors
from header import TokenStream
import pprint

row = 1


def is_space(ch):
    global row
    if ch == ' ' or ch == '\t':
        return True
    elif ch == '\r' or ch == '\n':
        row += 1
        return True


def trim_space(target: header.CharSequence):
    slen = len(target.stream)
    while target.pos < slen and is_space(target.stream[target.pos]):
        target.pos += 1


def create_new_row(row):
    row += 1


def parse_comment(context: header.CharSequence):
    context.pos += 1
    cur = context.pos
    str_len = len(context.stream)
    while cur < str_len and context.stream[cur] != '}':
        cur += 1
    if cur == len(context.stream):
        show_error(row, 'bracket not match ~')
    context.pos = cur + 1


def parse_ID_or_keyword(context: header.CharSequence, t_stream):
    global t_strea
    global row
    tok = header.Token()
    init_pos = context.pos
    while context.stream[context.pos].isalnum():
        context.pos += 1
    tok.row_number = row
    tok.text = context.stream[init_pos:context.pos]
    if tok.text in header.keywords:
        tok.type = header.TokenType.KEY_WORD
    else:
        tok.type = header.TokenType.ID
    t_stream.tokenStream.append(tok)


def parse_number(context: header.CharSequence, t_stream):
    global row
    tok = Token()
    init_pos = context.pos
    end_pos = len(context.stream)
    while context.pos < end_pos and context.stream[context.pos].isdigit():
        context.pos += 1
    tok.row_number = row
    tok.text = context.stream[init_pos:context.pos]
    tok.type = header.TokenType.NUM
    t_stream.tokenStream.append(tok)


single_char_token = {'=': TokenType.EQUAL, ';': TokenType.COLON,
                     '(': TokenType.LEFT_PAREN, ')': TokenType.RIGHT_PAREN,
                     '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR, '/': TokenType.DIV,
                     '.': TokenType.DOT, ',': TokenType.COMMA, '[': TokenType.LEFT_SQUARE_BRACKET,
                     ']': TokenType.RIGHT_SQUARE_BRACKET
                     }


def parse_rel_op(context: header.CharSequence, t_stream):
    cur_char = context.stream[context.pos]
    tok = Token()
    tok.row_number = row
    if context.stream[context.pos:context.pos + 2] == '>=':
        tok.type = TokenType.BIGGER_THAN_OR_EQUAL
        context.pos += 2
    elif context.stream[context.pos:context.pos + 2] == '<=':
        tok.type = TokenType.LESS_THAN_OR_EQUAL
        context.pos += 2
    elif cur_char == '>':
        tok.type = TokenType.BIGGER_THAN
        context.pos += 1
    elif cur_char == '<':
        tok.type = TokenType.LESS_THAN
        context.pos += 1
    t_stream.tokenStream.append(tok)


def parse_dual_op(context: header.CharSequence, t_stream):
    tok = Token()
    tok.row_number = row
    if context.stream[context.pos:context.pos + 2] == ':=':
        tok.type = TokenType.ASSIGN
    elif context.stream[context.pos:context.pos + 2] == '!=':
        tok.type = TokenType.NOT_EQUAL
    context.pos += 2
    t_stream.tokenStream.append(tok)


def scan(context: header.CharSequence):
    context.stream = context.stream.strip()
    seq_len = len(context.stream)
    t_stream = TokenStream()
    while context.pos < seq_len:
        trim_space(context)
        cur_char = context.stream[context.pos]
        if cur_char.isalpha():
            parse_ID_or_keyword(context, t_stream)
        elif cur_char.isdigit():
            parse_number(context, t_stream)
        elif cur_char in single_char_token:
            tok = Token()
            tok.row_number = row
            tok.type = single_char_token[cur_char]
            context.pos += 1
            t_stream.tokenStream.append(tok)
        elif cur_char == '{':
            parse_comment(context)
        elif cur_char in ('>', '<'):
            parse_rel_op(context, t_stream)
        elif context.stream[context.pos:context.pos + 2] in (':=', '!='):
            parse_dual_op(context, t_stream)
        else:
            show_error(t_stream.tokenStream[-1].row_number, 'unknown token~')
    return t_stream
