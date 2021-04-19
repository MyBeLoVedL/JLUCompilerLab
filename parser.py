#!/usr/bin/env python3
from numba import jit

from header import *
from exp import token_list_check, expect, parse_id_list
from lexer import scan
from smt import parse_statement


def parse_declaration(tokens: TokenStream):
    if tokens == 'procedure':
        return parse_procedure_dec(tokens)
    elif tokens == 'type':
        return parse_type_dec(tokens)
    else:
        return parse_variable_dec(tokens)
    return None


def parse_type_dec(tokens: TokenStream):
    return None

#! for each identifier,we store its name and row number


def parse_variable_dec(tokens: TokenStream):
    init_pos = tokens.pos
    kind = read_type(tokens)
    if kind is None:
        tokens.pos = init_pos
        return None

    varis = parse_id_list(tokens)
    token_list_check(tokens, [TokenType.COLON])
    tokens.read()
    dec = ASTnode(ASTtype.VARI_DEC)
    dec.VARI = {}

    for vari in varis:
        dec.VARI[(vari.text, vari.row_number)] = kind
    return dec


def read_type(tokens: TokenStream):
    ty = ''
    if tokens.verify_key('char') or tokens.verify_key('integer'):
        return tokens.read()
    elif tokens.verify_key('array'):
        return read_array_type(tokens)
    elif tokens.verify_key('record'):
        return read_record_type(tokens)


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
    tokens.read()
    ty.BASE_TYPE = tokens.read()
    return ty


#! VARIABLE is the dict of identifier and type

def read_record_type(tokens: TokenStream):
    token_list_check(tokens, ['record'])
    tokens.read()
    ty = ASTnode(ASTtype.RECORD)
    ty.VARIABLE = {}

    while tokens != 'end':
        kind = read_type(tokens)
        if kind is None:
            show_error(tokens.peek().row_number,
                       "expect at least one declaration~")
        varis = parse_id_list(tokens)
        token_list_check(tokens, [TokenType.COLON])
        tokens.read()
        for var in varis:
            ty.VARIABLE[(var.text, var.row_number)] = kind

    token_list_check(tokens, ['end'])
    tokens.read()
    return ty


def parse_para_list(tokens: TokenStream):
    para_list = []
    if tokens == TokenType.RIGHT_PAREN:
        return para_list

    if tokens == 'var':
        tokens.read()
    kind = read_type(tokens)
    if kind is None:
        show_error(tokens.peek().row_number,
                   "expect type here~")
    varis = parse_id_list(tokens)
    for var in varis:
        para_list.append((var.text, kind))

    while tokens != TokenType.RIGHT_PAREN:
        token_list_check(tokens, [TokenType.COLON])
        tokens.read()
        if tokens == 'var':
            tokens.read()
        kind = read_type(tokens)
        if kind is None:
            show_error(tokens.peek().row_number,
                       "expect at least one argument~")
        varis = parse_id_list(tokens)
        for var in varis:
            para_list.append((var.text, kind))
    return para_list

# ! PROCNAME as name of procedure


def parse_procedure_dec(tokens: TokenStream):
    token_list_check(tokens, ['procedure', TokenType.ID, TokenType.LEFT_PAREN])
    proc_blk = ASTnode(ASTtype.PROC_BLOCK)
    tokens.read()
    proc_blk.PROC_NAME = tokens.read()
    tokens.read()

    proc_blk.PARA_LIST = parse_para_list(tokens)
    token_list_check(tokens, [TokenType.RIGHT_PAREN, TokenType.COLON])
    tokens.read()
    tokens.read()

    proc_blk.DEC_LIST = []

    while True:
        dec = parse_declaration(tokens)
        if dec is None:
            break
        proc_blk.DEC_LIST.append(dec)

    token_list_check(tokens, ['begin'])
    tokens.read()

    proc_blk.SMT_LIST = []

    while True:
        smt = parse_statement(tokens)
        if smt is None:
            break
        proc_blk.SMT_LIST.append(smt)

    token_list_check(tokens, ['end'])
    tokens.read()

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
    # source_text = ' iden.age[add(1 * 23)] := 1 + 2 > 3 +2;'
    # source_text = 'add(1 * 23) ; '  # // bad text case
    # source_text = 'record array [1..2] of char a,b,c ;char d; end st1,st2;'
    # source_text = ')'
    source_text = """
        procedure add(integer a,b);
        integer c;
        begin 
            c := a+b;
            return c;
        end
    """
    set_text(source_text)
    parsed_text = source_text + '.'
    context = CharSequence(parsed_text)
    t_stream = scan(context)
    # show_tokens(t_stream)
    # tok = read_type(t_stream)
    # draw_ast_tree(tok)
    # smt.parse_arg_list()
    node = parse_declaration(t_stream)
    print(node.type)
    # draw_ast_tree(node)
    # for id, kind in node:
    #     print(f'{id} {kind}')
    # for (id, row), kind in node.VARI.items():
    #     print(f'{id} at row {row} of type {kind}')
    # print(type([]))
    # print('~'*40)
    # node2 = parse_statement(t_stream)
    # draw_ast_tree(node2)
