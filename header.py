#!/bin/python3

import enum


keywords = set(["program", "var", "integer", "char", "procedure", "begin", "end", "id", "array",
                "intc", "if", "then", "else", "fi", "while", "do", "endwh", "return", "array", "read", "write", "type"])


class TokenType(enum.Enum):
    ID = 0
    NUM = 1
    PLUS = 2
    MINUS = 3
    STAR = 4
    DIV = 5
    LEFT_PAREN = 6
    RIGHT_PAREN = 7
    LEFT_SQUARE_BRACKET = 8
    RIGHT_SQUARE_BRACKET = 9
    COLON = 10
    DOT = 11
    LESS_THAT = 12
    BIGGER_THAN = 13
    EQUAL = 14
    LEFT_BRACKET = 15
    RIGHT_BRACKET = 16
    ASSIGN = 17
    SINGLE_QUOTE = 18
    DOUBLE_QUOTE = 19
    KEY_WORD = 20
    UNKNOWN = 21,
    SEMI_COLON = 22


class CharSequence:
    def __init__(self, chars):
        self.stream = chars
        self.pos = 0


class Token:
    def __init__(self, row_number=1, type=TokenType.UNKNOWN, text=''):
        self.row_number = row_number
        self.type = type
        self.text = text


class TokenStream:
    def __init__(self):
        self.tokenStream = []
