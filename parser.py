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

    while tokens.peek().type == TokenType.STAR or tokens.peek().type == TokenType.DIV:
        tmp = ASTnode(ASTtype.MUL_EXP)
        if tokens.peek().type == TokenType.STAR:
            tmp.text = '*'
        else:
            tmp.text = r'/'

        tokens.read()
        right = match_pri(tokens)
        if right is None:
            show_error(
                source_text, tokens.tokenStream[tokens.pos].row_number, 'Expect axpression after mul operator')

        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_add(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_mul(tokens)

    while tokens.peek().type == TokenType.PLUS or tokens.peek().type == TokenType.MINUS:
        tmp = ASTnode(ASTtype.ADD_EXP)
        if tokens.peek().type == TokenType.PLUS:
            tmp.text = '+'
        else:
            tmp.text = '-'
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


def match_rel_low_priority(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_mul(tokens)

    while tokens.peek().type in (TokenType.LESS_THAT, TokenType.BIGGER_THAN, TokenType.LESS_THAN_OR_EQUAL, TokenType.BIGGER_THAN_OR_EQUAL):
        tmp = ASTnode(ASTtype.REL_EXP)
        if tokens.peek().type == TokenType.BIGGER_THAN:
            tmp.text = '>'
        elif tokens.peek().type == TokenType.LESS_THAT:
            tmp.text = '<'
        elif tokens.peek().type == TokenType.BIGGER_THAN_OR_EQUAL:
            tmp.text = '>='
        elif tokens.peek().type == TokenType.LESS_THAN_OR_EQUAL:
            tmp.text = '<='

        tokens.read()
        right = match_pri(tokens)
        if right is None:
            show_error(
                source_text, tokens.tokenStream[tokens.pos].row_number, 'Expect axpression after relational  operator')
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_rel(tokens: TokenStream):
    init_pos = tokens.pos
    left = match_rel_low_priority(tokens)

    while tokens.peek().type in (TokenType.EQUAL, TokenType.NOT_EQUAL):
        tmp = ASTnode(ASTtype.REL_EXP)
        if tokens.peek().type == TokenType.EQUAL:
            tmp.text = '='
        elif tokens.peek().type == TokenType.NOT_EQUAL:
            tmp.text = '!='

        tokens.read()
        right = match_rel_low_priority(tokens)
        if right is None:
            show_error(
                source_text, tokens.tokenStream[tokens.pos].row_number, 'Expect axpression after relational  operator')
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


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
    # source_text = ''.join(lines)
    # source_text = '(1 + 2 ) >= (4 + 2 * 2)  = true ;'
    source_text = ' 1 > 2 = 3 > 4;'
    context = CharSequence(source_text)
    scan(context)
    show_tokens(t_stream)
    node = match_rel(t_stream)
    draw_ast_tree(node)
