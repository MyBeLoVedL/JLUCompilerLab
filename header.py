#!/bin/python3

import enum


keywords = set(["program", "var", "integer", "char", "procedure", "begin", "end", "id", "array",
                "intc", "if", "then", "else", "fi", "while", "do", "endwh", "return", "array", "read", "write", "type"])


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
        self.pos = 0

    def peek(self):
        return self.tokenStream[self.pos]

    def read(self):
        res = self.tokenStream[self.pos]
        self.pos += 1
        return res

    def unread(self, num=1):
        self.pos -= num

    def reset_pos(self, pos):
        self.pos = pos


class ASTnode:
    def __init__(self, type):
        self.type = type
        self.child = []

    def addChild(self, child):
        self.child.append(child)


class ASTtype(enum.Enum):
    MUL_EXP = 0
    ADD_EXP = 1
    PRI_EXP = 2


def show_error(text, line_num, msg):
    lines = text.split('\n')
    i = 0
    for i in range(line_num - 1):
        print(' '*10 + lines[i])
    i += 1
    print(bcolors().FAIL+'>>>>>'.ljust(9, ' ')+bcolors.ENDC, end=' ')
    print(lines[i])
    print()
    print()
    print(bcolors.OKGREEN + msg + bcolors.ENDC)
    exit()


def show_tokens(t_stream: TokenStream):
    for tok in t_stream.tokenStream:
        print(
            'rows:'+bcolors.WARNING +
            f'{tok.row_number}'.ljust(6, ' ') + bcolors.WARNING
            + 'type: ' + bcolors.OKBLUE +
            str(tok.type).ljust(26, ' ') + bcolors.OKBLUE
            + 'text:  ' + bcolors.OKGREEN +
            tok.text.ljust(10, ' ') + bcolors.ENDC
        )


def draw_ast_tree(root):
    draw_ast_tree_helper(root, ' ')


def draw_ast_tree_helper(root, sep):
    if root is None:
        return
    if type(root) == ASTnode:
        print(sep + str(root.type) + ':')
        for c in root.child:
            draw_ast_tree_helper(c, sep + ' '*4)
    else:
        print(sep + bcolors.WARNING + str(root.type).ljust(5) +
              bcolors.OKGREEN + root.text.rjust(5))
