#!/bin/python3

import header
from header import TokenType
from header import Token


t_stream = header.TokenStream()


def is_space(ch):
    return ch == ' ' or ch == '\n' or ch == '\r' or ch == '\t'


def trim_space(target: header.CharSequence):
    while is_space(target.stream[target.pos]):
        target.pos += 1


def parse_ID_or_keyword(context: header.CharSequence):
    global t_stream
    tok = header.Token()
    init_pos = context.pos
    while context.stream[context.pos].isalnum():
        context.pos += 1
    tok.text = context.stream[init_pos:context.pos]
    if tok.text in header.keywords:
        tok.type = header.TokenType.KEY_WORD
    else:
        tok.type = header.TokenType.ID
    t_stream.tokenStream.append(tok)


def parse_number(context: header.CharSequence):
    global t_stream
    tok = header.Token
    init_pos = context.pos
    while context.stream[context.pos].isdigit():
        context.pos += 1
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
            tok.type = single_char_token[cur_char]
            context.pos += 1
            t_stream.tokenStream.append(tok)
        elif context.stream[context.pos:context.pos + 2] == ':=':
            tok = Token()
            tok.type = TokenType.ASSIGN
            context.pos += 2
            t_stream.tokenStream.append(tok)


if __name__ == '__main__':
    # scan("int age = 10;")
    with open('simple.snl', 'r') as f:
        lines = f.readlines()
        print(lines)

    context = header.CharSequence(''.join(lines))
    print(context.stream)
    scan(context)
    for tok in t_stream.tokenStream:
        print(f'type : {tok.type} text: {tok.text}')
    print(context.pos)
