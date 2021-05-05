#!/usr/bin/env python3

from header import *
from exp import match_pri, token_list_check, expect, parse_id_list
from lexer import scan
from smt import parse_loop_statement, parse_statement


def parse_declaration(tokens: TokenStream):
    if tokens == 'procedure':
        return parse_procedure_dec(tokens)
    elif tokens == 'type':
        return parse_type_dec(tokens)
    elif tokens == 'var':
        return parse_variable_dec(tokens)
    return None


def parse_type_dec(tokens: TokenStream):
    global scope, table, level
    tokens.read()
    ty = ASTnode(ASTtype.TYPE_DEC)
    ty.DEC = {}

    while True:
        token_list_check(tokens, [TokenType.ID, TokenType.EQUAL])
        id = tokens.read().text
        tokens.read()
        kind = read_type(tokens)
        if kind is None:
            show_error(tokens.peek().row_number, "not valid type declaration~")
        if table_walk(id) >= 0:
            show_error(tokens.peek().row_number,
                       f'symbol {id} redefinition')
        ty.DEC[id] = kind
        p = Sym_type(id, kind)
        table.append(p)
        if tokens != TokenType.COMMA:
            break
        tokens.read()

    token_list_check(tokens, [TokenType.COLON])
    tokens.read()
    return ty


#! for each identifier,we store its name and row number


def parse_variable_dec(tokens: TokenStream):
    global scope, table, level
    init_pos = tokens.pos
    token_list_check(tokens, ['var'])
    tokens.read()
    kind = read_type(tokens)
    if kind is None:
        tokens.pos = init_pos
        return None
    varis = parse_id_list(tokens)
    row = tokens.peek().row_number
    for v in varis:
        if level_walk(v.text) >= 0:
            show_error(row,
                       f'symbol {v.text} redefinition')
        p = Sym_vari(v.text, kind, level, None)
        table.append(p)
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
    elif tokens == TokenType.ID:
        return tokens.read()
    else:
        show_error(tokens.peek().row_number, 'unknown type ~')


def read_array_type(tokens: TokenStream):
    token_list_check(tokens, [
        'array', TokenType.LEFT_SQUARE_BRACKET, TokenType.NUM, TokenType.DOT,
        TokenType.DOT, TokenType.NUM, TokenType.RIGHT_SQUARE_BRACKET, 'of',
        ('char', 'integer')
    ])
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
        show_error(tokens.peek().row_number, "expect type here~")
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
    global scope, table, level
    level += 1
    token_list_check(tokens, ['procedure', TokenType.ID, TokenType.LEFT_PAREN])
    proc_blk = ASTnode(ASTtype.PROCEDURE)
    tokens.read()
    proc_blk.PROC_NAME = tokens.read().text
    tokens.read()

    proc_blk.PARA_LIST = parse_para_list(tokens)
    p = Sym_proc(proc_blk.PROC_NAME, None, level, proc_blk.PARA_LIST)
    if table_walk(p.text) >= 0:
        print(f'redef pos {table_walk(p.text)}')
        show_error(tokens.peek().row_number,
                   f'symbol {p.text} redefinition')
    table.append(p)
    scope.append(len(table))

    row = tokens.peek().row_number
    for para in proc_blk.PARA_LIST:
        if level_walk(para[0]) >= 0:
            show_error(row,
                       f'symbol {para[0]} redefinition')
        arg = Sym_vari(para[0], para[1], level, None)
        table.append(arg)

    token_list_check(tokens, [TokenType.RIGHT_PAREN, TokenType.COLON])
    tokens.read()
    tokens.read()

    proc_blk.DEC_list, proc_blk.SMT_LIST = parse_dec_body(tokens)
    table.append(scope[-1]-1)
    del scope[-1]
    level -= 1

    return proc_blk


def parse_dec_body(tokens: TokenStream):

    DEC_LIST = []

    while True:
        dec = parse_declaration(tokens)
        if dec is None:
            break
        DEC_LIST.append(dec)

    token_list_check(tokens, ['begin'])
    tokens.read()

    SMT_LIST = []

    while True:
        smt = parse_statement(tokens)
        if smt is None:
            break
        SMT_LIST.append(smt)

    token_list_check(tokens, ['end'])
    tokens.read()

    return (DEC_LIST, SMT_LIST)


def __llparse(t_stream: TokenStream) -> ASTnode:
    global scope, table, level
    token_list_check(t_stream, ['program', TokenType.ID])
    prog = ASTnode(ASTtype.PROGRAM)
    t_stream.read()
    prog.PROG_NAME = t_stream.read().text
    scope.append(0)
    p = Sym_vari(prog.PROG_NAME, None, 0)
    table.append(p)
    level += 1
    prog.DEC_LIST, prog.SMT_LIST = parse_dec_body(t_stream)
    table.append(0)
    return prog


def __lrparse(t_stream: TokenStream) -> ASTnode:
    pass


if __name__ == '__main__':
    lines = []
    with open('simple.snl', 'r') as f:
        lines = f.readlines()
    source_text = ''.join(lines)
    # source_text = 'a[1 + 2] := 20;'
    # source_text = '(1 + 2 ) >= (4 + 2 * 2)  = true ;'
    # source_text = 'add(1 + 2,1*2 );\nif 1 > 2 then a = 10; else a = 20; fi'
    # source_text = 'add(12 + 32*12 ,101);  '
    # source_text = ' iden.age[add(1 * 23)] := 1 + 2 > 3 +2;'
    # source_text = 'add(1 * 23) ; '  # // bad text case
    # source_text = 'record array [1..2] of char a,b,c ;char d; end st1,st2;'
    # source_text = ')'
    # source_text = """
    #         while k < j do
    #             if a[k + 1] < a[k]
    #             then
    #                 t := a[k];
    #                 a[k] := a[k + 1];
    #                 a[k + 1] := t;
    #             else  temp := 0;
    #             fi;
    #         k := k + 1;
    #         endwh;
    # """
    # source_text = "type t = integer,c = char,stu = record char a;integer age;end"
    source_text = """
      procedure sub(integer a;integer b);
        var integer res;
        var char ch;
        begin 
            res := (a + b) > 20 = 1 > 2;
            return res;
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
    # node = __llparse(t_stream)
    node = parse_procedure_dec(t_stream)
    # node = parse_procedure_dec(t_stream)

    # for v in table:
    #     if type(v) is str:
    #         print('str: ' + v)
    #     elif type(v) is int:
    #         print(v)
    #     else:
    #         print(v.text)
    # print(f"index : {table_walk('t')}")
    # node = match_pri(t_stream)
    # node = parse_statement(t_stream)
    # node3 = parse_statement(t_stream)
    # print(node.type)
    draw_ast_tree(node)
    # print(node.INDEX)
    # for id, kind in node.DEC.items():
    #     print(f'{id} {kind}')
    # for (id, row), kind in node.VARI.items():
    #     print(f'{id} at row {row} of type {kind}')
    # print(type([]))
    # print('~'*40)
    # node2 = parse_statement(t_stream)
    # draw_ast_tree(node2)
