#!/bin/python3

import header
from header import TokenType
from header import Token
from header import bcolors
import pprint

t_stream = header.TokenStream()
row = 1


def is_space(ch):
    global row
    if ch == ' ' or ch == '\t':
        return True
    elif ch == '\r' or ch == '\n':
        row += 1
        return True


def trim_space(target: header.CharSequence):
    while is_space(target.stream[target.pos]):
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
        show_error('comment bracket not match !~')
    context.pos = cur + 1


def parse_ID_or_keyword(context: header.CharSequence):
    global t_stream
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


def parse_number(context: header.CharSequence):
    global t_stream
    global row
    tok = Token()
    init_pos = context.pos
    while context.stream[context.pos].isdigit():
        context.pos += 1
    tok.row_number = row
    tok.text = context.stream[init_pos:context.pos]
    tok.type = header.TokenType.NUM
    t_stream.tokenStream.append(tok)


single_char_token = {'=': TokenType.EQUAL, ';': TokenType.COLON,
                     '(': TokenType.LEFT_PAREN, ')': TokenType.RIGHT_PAREN,
                     '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.STAR, '/': TokenType.DIV,
                     '.': TokenType.DOT
                     }


def scan(context: header.CharSequence):
    seq_len = len(context.stream)
    while context.pos < seq_len:
        trim_space(context)
        cur_char = context.stream[context.pos]
        if cur_char.isalpha():
            parse_ID_or_keyword(context)
        elif cur_char.isdigit():
            parse_number(context)
        elif cur_char in single_char_token:
            tok = Token()
            tok.row_number = row
            tok.type = single_char_token[cur_char]
            context.pos += 1
            t_stream.tokenStream.append(tok)
        elif cur_char == '{':
            parse_comment(context)
        elif context.stream[context.pos:context.pos + 2] == ':=':
            tok = Token()
            tok.row_number = row
            tok.type = TokenType.ASSIGN
            context.pos += 2
            t_stream.tokenStream.append(tok)
