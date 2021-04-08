import header
import lexer
from header import Token
from header import TokenType
"""
parse expressions
"""

#!/usr/bin/env python3

"""
parse expressions
"""
from header import *
from lexer import *

source_text = ''


def match_pri(tokens: TokenStream):
    tmp = ASTnode(ASTtype.PRI_EXP)

    if tokens.peek().type == TokenType.ID:
        tmp.addChild(tokens.read())
    elif tokens.peek().type == TokenType.NUM:
        tmp.addChild(tokens.read())
    elif tokens.peek().type == TokenType.LEFT_PAREN:
        tokens.read()
        child = match_add(tokens)
        if child is None:
            tokens.reset_pos(init_pos)
            return child
        if tokens.peek().type != TokenType.RIGHT_PAREN:
            show_error(
                source_text, tokens.tokenStream[tokens.pos].row_number, 'mis-matched parenthesis~')
        else:
            tmp.addChild(child)
            tokens.read()
    if len(tmp.child) == 0:
        return None
    else:
        return tmp


def match_mul(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_pri(tokens)

    while tokens.peek().type == TokenType.STAR:
        tokens.read()
        right = match_pri(tokens)
        if right is None:
            show_error(
                source_text, tokens.tokenStream[tokens.pos].row_number, 'Expect axpression after mul operator')
        tmp = ASTnode(ASTtype.MUL_EXP)
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_add(tokens):
    init_pos = tokens.pos

    left = match_mul(tokens)

    while tokens.peek().type == TokenType.PLUS:
        tokens.read()
        right = match_add(tokens)
        if right is None:
            show_error(
                source_text, tokens.tokenStream[tokens.pos].row_number, 'Expect axpression after plus operator')
        tmp = ASTnode(ASTtype.ADD_EXP)
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_rel():
    return


def match_logic():
    return


def match_exp():
    return


"""
parse statements
"""


def parse_simple_statement():
    return


def parse_assign_statement():
    return


def parse_return_statement():
    return


def parse_IO_statement():
    return


def parse_loop_statement():
    return


def parse_condition_statement():
    return


"""
parse declarations
"""


def parse_variable():
    return


def parse_type():
    return


def parse_procedure():
    return


if __name__ == '__main__':

    lines = []
    with open('simple.snl', 'r') as f:
        lines = f.readlines()
    source_text = ''.join(lines)
    source_text = 'a * (10  + 12) * 32 + 1;'
    context = CharSequence(source_text)

    scan(context)
    node = match_add(t_stream)
    draw_ast_tree(node)
