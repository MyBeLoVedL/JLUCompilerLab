#!/bin/python3

import enum


keywords = set(["program", "var", "integer", "char", "procedure", "begin", "end", "id", "array",
                "intc", "if", 'fi', "then", "else", "fi", "while", "do", "endwh", "return", "array", "read", "write", "type", "of", "record"])

to_be_parsed_text = 'hem'


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
    SEMI_COLON = 22,
    LESS_THAN_OR_EQUAL = 23,
    BIGGER_THAN_OR_EQUAL = 24
    NOT_EQUAL = 25
    COMMA = 26


class CharSequence:
    def __init__(self, chars):
        self.stream = chars
        self.pos = 0


class Token:
    def __init__(self, row_number=1, type=TokenType.UNKNOWN, text=''):
        self.row_number = row_number
        self.type = type
        self.text = text

    def __eq__(self, other):
        if type(other) == str:
            return self.type == TokenType.KEY_WORD and self.text == other
        else:
            return self.type == other

    def __str__(self) -> str:
        if self.type == TokenType.KEY_WORD:
            return f'{self.text}'
        else:
            return f'{self.text} {self.type}'


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

    def not_empty(self):
        return self.pos < len(self.tokenStream)

    def look_behind(self, i):
        return self.tokenStream[self.pos + i]

    def verify_key(self, keyword: str):
        return self.peek().type == TokenType.KEY_WORD and self.peek().text == keyword

    def __eq__(self, other):
        return self.tokenStream[self.pos] == other


class ASTnode:
    def __init__(self, type, text=''):
        self.type = type
        self.text = text
        self.child = []

    def addChild(self, child):
        self.child.append(child)

    def __str__(self) -> str:
        return f'{self.text} type{self.type}'


class ASTtype(enum.Enum):
    MUL_EXP = 0
    ADD_EXP = 1
    PRI_EXP = 2
    REL_EXP = 3
    SIMPLE_SMT = 4
    RET_SMT = 5
    ASSIGN_SMT = 6
    COND_SMT = 7
    LOOP_SMT = 8
    INPUT_SMT = 9
    OUTPUT_SMT = 10
    FUNC_CALL = 11
    ASG_SMT = 12
    PROC_BLOCK = 13
    PARAMETER = 14
    ARRAY = 15
    RECORD = 16
    VARI_DEC = 17
    TYPE_DEC = 18


def set_text(text):
    global to_be_parsed_text
    to_be_parsed_text = text


def show_error(line_num, msg):
    global to_be_parsed_text
    lines = to_be_parsed_text.split('\n')
    i = -1
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
    for tok in t_stream.tokenStream[t_stream.pos:]:
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
        if root.type == ASTtype.FUNC_CALL:
            print(sep + f'( function name: {root.FUNC_NAME.text}',
                  end=bcolors.WARNING + ' args: ' + bcolors.ENDC)
            for arg in root.ARG_LIST:
                print(str(arg.type), end=' ')
        elif root.type == ASTtype.ASG_SMT:
            # print(sep + str(root.type) + ':')
            print(sep + '   ' + root.VARI.text, end='')
            if root.STRUCT is not None:
                print('.' + root.STRUCT.text, end='')
            if root.ARR_INDEX is not None:
                print(f'[{str(root.ARR_INDEX.type)}]', end='')
            print(' := ' + str(root.EXP.type))

        for c in root.child:
            draw_ast_tree_helper(c, sep + ' '*4)
    else:
        print(sep + bcolors.WARNING + str(root.type).ljust(5) +
              bcolors.OKGREEN + root.text.rjust(5))
