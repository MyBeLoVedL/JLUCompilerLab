#!/usr/bin/env python3
from numba import jit

from header import *
from exp import token_list_check, expect
from lexer import scan
from smt import parse_statement


def parse_declaration(tokens: TokenStream):
    pass


def parse_variable(tokens: TokenStream):
    # {name, type}
    declared_variables = {}
    assert (tokens.peek().type ==
            TokenType.KEY_WORD and tokens.peek().text == 'var')
    tokens.read()
    if tokens.peek().type is None:
        show_error(tokens.peek().row_number, "the type of identifier cannot be null");
    tokens.read()
    if tokens.peek().text is None:
        show_error(tokens.peek().row_number, "the name of identifier cannot be null")
    if tokens.peek().text in declared_variables:
        show_error(tokens.peek().row_number, "the variable has already been declared")
    else:
        declared_variables[tokens.text] = tokens.type
    return declared_variables


def parse_type():
    return


def read_array_type(tokens: TokenStream):
    token_list_check(tokens, ['array',
                              TokenType.LEFT_SQUARE_BRACKET,  TokenType.NUM, TokenType.DOT, TokenType.DOT, TokenType.NUM, TokenType.RIGHT_SQUARE_BRACKET, 'of', ('char', 'integer')])
    ty = ASTnode(ASTtype.ARRAY)
    tokens.read()
    tokens.read()
    ty.LOWER_BOUND = tokens.read()
    tokens.read()
    tokens.read()
    ty.UPPER_BOUND = tokens.read()
    tokens.read()
    ty.BASE_TYPE = tokens.read()
    return ty


#! VARIABLE is the dict of identifier and type

def read_record_type(tokens: TokenStream):
    token_list_check(tokens, 'record')
    tokens.read()
    ty = ASTnode(ASTtype.RECORD)
    ty.VARIABLE = {}

    kind = read_type(tokens)
    vari = tokens.read()

    ty.VARIABLE[vari.text] = kind

    while tokens.peek().type != TokenType.COLON:
        if tokens.peek().type != TokenType.COMMA:
            show_error(tokens.peek().row_number,
                       'expect comma to seperate identifiers~')
        tokens.read()
        vari = tokens.read()
        ty.VARIABLE[vari.text] = kind

    token_list_check(tokens, 'end')
    tokens.read()


def read_type(tokens: TokenStream):
    ty = ''
    if tokens.verify_key('char') or tokens.verify_key('integer'):
        return tokens.read()
    elif tokens.verify_key('array'):
        return read_array_type(tokens)
    elif tokens.verify_key('record'):
        pass


def parse_para_list(tokens: TokenStream):
    para_list = []

    pass

# ! PROCNAME as name of procedure


def parse_procedure(tokens: TokenStream):
    assert tokens.peek().type == TokenType.KEY_WORD and tokens.peek().text == 'procedure'
    tokens.read()

    proc_blk = ASTnode(ASTtype.PROC_BLOCK)
    proc_blk.PROC_NAME = expect(
        tokens, TokenType.ID, 'expect procedure name ~')
    expect(tokens, TokenType.LEFT_PAREN, 'expect left parenthesis~')
    proc_blk.PARA_LIST = parse_para_list(tokens)
    expect(tokens, TokenType.RIGHT_PAREN, 'expect left parenthesis~')

    proc_blk.PARA_LIST = []
    dec = ''
    while dec is not None:
        dec = parse_declaration(tokens)
        if dec is None:
            proc_blk.PARA_LIST.append(dec)

    expect(tokens, TokenType.KEY_WORD and tokens.peek().text == 'begin')

    proc_blk.SMT_LIST = []
    smt = ''

    while smt is not None:
        smt = parse_statement(tokens)
        if smt is not None:
            proc_blk.SMT_LIST.append(smt)

    expect(tokens, TokenType.KEY_WORD and tokens.peek().text == 'end')

    return proc_blk


def __llparse(t_stream: TokenStream) -> ASTnode:
    pass


def __lrparse(t_stream: TokenStream) -> ASTnode:
    pass


if __name__ == '__main__':
    lines = []
    with open('simple.snl', 'r') as f:
        lines = f.readlines()
    # source_text = ''.join(lines)
    # source_text = '(1 + 2 ) >= (4 + 2 * 2)  = true ;'
    # source_text = 'add(1 + 2,1*2 );\nif 1 > 2 then a = 10; else a = 20; fi'
    # source_text = 'add(12 + 32*12 ,101);  '
    source_text = ' iden.age[add(1 * 23)] := 1 + 2 > 3 +2;'
    # source_text = 'add(1 * 23) ; '  # // bad text case
    # source_text = 'array [1..2] of char;'
    set_text(source_text)
    parsed_text = source_text + '.'
    context = CharSequence(parsed_text)
    t_stream = scan(context)
    show_tokens(t_stream)
    # tok = read_type(t_stream)
    # draw_ast_tree(tok)
    # smt.parse_arg_list()
    node = parse_statement(t_stream)
    draw_ast_tree(node)
    print()
    # print(type([]))
    # print('~'*40)
    node2 = parse_statement(t_stream)
    draw_ast_tree(node2)
