#!/usr/bin/env python3
from numba import jit

"""
parse expressions
"""
from header import *
from lexer import *

from cyberbrain import trace

source_text = ''


def expect(tokens, target_token_type, error_msg):
    if tokens.peek().type != target_token_type:
        show_error(tokens.peek().row_number, error_msg)
    return tokens.read()


def parse_arg_list(tokens: TokenStream):
    tmp = []
    if tokens.peek().type != TokenType.RIGHT_PAREN:
        first_arg = match_rel(tokens)
        tmp.append(first_arg)
    while tokens.peek().type != TokenType.RIGHT_PAREN:
        expect(tokens, TokenType.COMMA,
               'use comma to seperate multiple arguments ~')
        arg = match_rel(tokens)
        tmp.append(arg)
    return tmp


def token_list_check(tokens: TokenStream, target_list):
    l_len = len(target_list)

    for i in range(l_len):
        if type(target_list[i]) == str:
            if not (tokens.look_behind(i).type, tokens.look_behind(i).text) == (TokenType.KEY_WORD, target_list[i]):
                show_error(
                    tokens.look_behind(i).row_number, f'expect {target_list[i]} here~ ')
            else:
                continue
        elif type(target_list[i]) is tuple:
            if not (tokens.look_behind(i).type is TokenType.KEY_WORD and tokens.look_behind(i).text in target_list[i]):
                types = ' or '.join(target_list[i])
                show_error(
                    tokens.look_behind(i).row_number, f'expect {types}  here~~ ')
            else:
                continue

        elif tokens.look_behind(i).type != target_list[i]:
            show_error(
                tokens.tokenStream[tokens.pos + i].row_number, f'expect {str(target_list[i])} here~! ')


def match_pri(tokens: TokenStream):
    tmp = None
    init_pos = tokens.pos
    if tokens == TokenType.ID:
        tmp = tokens.read()
        if tokens == TokenType.LEFT_PAREN:
            func_name = tmp
            tmp = ASTnode(ASTtype.FUNC_CALL)
            tmp.FUNC_NAME = func_name
            tokens.read()
            tmp.ARG_LIST = parse_arg_list(tokens)
            expect(tokens, TokenType.RIGHT_PAREN, 'expect right parenthesis ~')

    elif tokens == TokenType.NUM:
        tmp = tokens.read()
    elif tokens == TokenType.LEFT_PAREN:
        tokens.read()
        child = match_rel(tokens)
        if child is None:
            tokens.reset_pos(init_pos)
            return child
        expect(tokens, TokenType.RIGHT_PAREN, 'mis-matched parenthesis~')
        tmp = child
    return tmp


def match_mul(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_pri(tokens)

    while tokens == TokenType.STAR or tokens == TokenType.DIV:
        tmp = ASTnode(ASTtype.MUL_EXP)
        if tokens.peek().type == TokenType.STAR:
            tmp.text = '*'
        else:
            tmp.text = r'/'

        tokens.read()
        right = match_pri(tokens)
        if right is None:
            show_error(
                tokens.tokenStream[tokens.pos].row_number, 'Expect expression after mul operator')

        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_add(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_mul(tokens)

    while tokens.not_empty() and (tokens.peek().type == TokenType.PLUS or tokens.peek().type == TokenType.MINUS):
        tmp = ASTnode(ASTtype.ADD_EXP)
        if tokens.peek().type == TokenType.PLUS:
            tmp.text = '+'
        else:
            tmp.text = '-'
        tokens.read()
        right = match_add(tokens)
        if right is None:
            show_error(
                tokens.tokenStream[tokens.pos - 1].row_number, 'Expect expression after plus operator')
        tmp = ASTnode(ASTtype.ADD_EXP)
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_rel_low_priority(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_add(tokens)

    while tokens.not_empty() and tokens.peek().type in (TokenType.LESS_THAT, TokenType.BIGGER_THAN, TokenType.LESS_THAN_OR_EQUAL, TokenType.BIGGER_THAN_OR_EQUAL):
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
        right = match_add(tokens)
        if right is None:
            show_error(
                tokens.tokenStream[tokens.pos].row_number, 'Expect expression after relational  operator')
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_rel(tokens: TokenStream):
    init_pos = tokens.pos
    left = match_rel_low_priority(tokens)

    while tokens.not_empty() and tokens.peek().type in (TokenType.EQUAL, TokenType.NOT_EQUAL):
        tmp = ASTnode(ASTtype.REL_EXP)
        if tokens.peek().type == TokenType.EQUAL:
            tmp.text = '='
        elif tokens.peek().type == TokenType.NOT_EQUAL:
            tmp.text = '!='

        tokens.read()
        right = match_rel_low_priority(tokens)
        if right is None:
            show_error(
                tokens.tokenStream[tokens.pos].row_number, 'Expect expression after relational  operator')
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


def parse_statement(tokens: TokenStream):
    if tokens.peek().type == TokenType.KEY_WORD and tokens.peek().text == 'return':
        return parse_return_statement(tokens)
    elif tokens.peek().type == TokenType.KEY_WORD and tokens.peek().text == 'if':
        return parse_condition_statement(tokens)
    elif tokens.peek().type == TokenType.KEY_WORD and tokens.peek().text == 'while':
        return parse_loop_statement(tokens)
    elif tokens.peek().type == TokenType.KEY_WORD and tokens.peek().text in ('read', 'write'):
        return parse_IO_statement
    else:
        # ! if match failed,should not consume any token
        smt = None
        if tokens.peek().type == TokenType.ID:
            smt = parse_assign_statement(tokens)
        if smt is None:
            smt = parse_simple_statement(tokens)
        return smt


def parse_simple_statement(tokens: TokenStream):
    init_pos = tokens.pos
    smt = ASTnode(ASTtype.SIMPLE_SMT)
    child = match_rel(tokens)
    if child is None:
        tokens.pos = init_pos
        return None
    smt.addChild(child)

    if not tokens.not_empty() or tokens.peek().type != TokenType.COLON:
        show_error(tokens.tokenStream[tokens.pos - 1].row_number,
                   'expect colon at the end of a statement ~')
    tokens.read()
    return smt

# ! VARI is the name of identifier,STRUCT if possible struct member,ARR_INDEX is possible array index


def parse_assign_statement(tokens: TokenStream):
    init_pos = tokens.pos
    asg_smt = ASTnode(ASTtype.ASG_SMT)

    assert(tokens.peek().type == TokenType.ID)
    asg_smt.VARI = tokens.read()

    if tokens.peek().type == TokenType.DOT:
        tokens.read()
        expect(tokens, TokenType.ID, 'expect identifier at struct position')
        tokens.unread()
        asg_smt.STRUCT = tokens.read()

    if tokens.peek().type == TokenType.LEFT_SQUARE_BRACKET:
        tokens.read()
        exp = match_rel(tokens)
        if exp is None:
            show_error(tokens.tokenStream[tokens.pos].row_number,
                       'expect expression between square bracket')
        if tokens.peek().type != TokenType.RIGHT_SQUARE_BRACKET:
            show_error(
                tokens.tokenStream[tokens.pos].row_number, 'mismatched square bracket~')
        tokens.read()
        asg_smt.ARR_INDEX = exp

    if tokens.peek().type != TokenType.ASSIGN:
        tokens.pos = init_pos
        return None

    expect(tokens, TokenType.ASSIGN, 'expect assign operator ~')

    val = match_rel(tokens)

    if val is None:
        show_error(
            tokens.tokenStream[tokens.pos].row_number, 'expect expression after assign')
    asg_smt.EXP = val

    expect(tokens, TokenType.COLON, 'expect colon ~')

    return asg_smt


def parse_return_statement(tokens: TokenStream):
    smt = ASTnode(ASTtype.RET_SMT)
    tok = tokens.peek()
    assert(tok.type == TokenType.KEY_WORD and tok.text == 'return')
    tokens.read()
    smt.addChild(match_rel(tokens))
    if not tokens.not_empty() or tokens.peek().type != TokenType.COLON:
        show_error(tokens.tokenStream[tokens.pos - 1].row_number,
                   'expect colon at the end of a statement ~')
    tokens.read()
    return smt


def parse_IO_statement(tokens: TokenStream):
    if tokens.peek().text == 'read':
        io_smt = ASTnode(ASTtype.INPUT_SMT)
        tokens.read()
        if tokens.peek().type != TokenType.LEFT_PAREN:
            show_error(tokens.peek().row_number, 'expect parenthesis~')
        tokens.read()

        if tokens.type == TokenType.ID:
            show_error(tokens.peek().row_number,
                       'expect an identifier in read statement ~')
        # ! for astnode with single statement ,we use child directly
        io_smt.addChild(tokens.read())

        if tokens.peek().type != TokenType.RIGHT_PAREN:
            show_error(tokens.peek().row_number, 'expect parenthesis~')
        tokens.read()
    elif tokens.peek().text == 'write':
        io_smt = ASTnode(ASTtype.OUTPUT_SMT)
        tokens.read()
        if tokens.peek().type != TokenType.LEFT_PAREN:
            show_error(tokens.peek().row_number, 'expect parenthesis~')
        tokens.read()

        exp = match_rel(tokens)
        if exp is None:
            show_error(tokens.peek().row_number,
                       'expression between output statement')
        io_smt.addChild(exp)

        if tokens.peek().type != TokenType.RIGHT_PAREN:
            show_error(tokens.peek().row_number, 'expect parenthesis~')
        tokens.read()

    return io_smt


def parse_loop_statement(tokens: TokenStream):
    assert (tokens.peek().type ==
            TokenType.KEY_WORD and tokens.peek().text == 'while')
    tokens.read()
    loop_smt = ASTnode(ASTtype.LOOP_SMT)
    cond = match_rel(tokens)
    if cond is None:
        show_error(tokens.peek().row_number, 'condition can\'t be null')
    if tokens.peek().type != TokenType.KEY_WORD or tokens.peek().text != 'do':
        show_error(tokens.peek().row_number, 'expect do after condition')

    tokens.read()

    child_smt = parse_statement(tokens)
    if child_smt is None:
        show_error(tokens.peek().row_number, 'expect at least one statement ~')
    loop_smt.COND_EXP = cond
    loop_smt.LOOP_SMT = []
    loop_smt.LOOP_SMT.append(child_smt)

    while True:
        child_smt = parse_statement(tokens)
        if child_smt is None:
            break
        loop_smt.LOOP_SMT.append(child_smt)
    if tokens.peek().type != TokenType.KEY_WORD or tokens.peek().text != 'endwh':
        show_error(tokens.peek().row_number,
                   'expect \'endwh\' at the end of if statement~')

    return loop_smt


def parse_condition_statement(tokens: TokenStream):
    assert (tokens.peek().type ==
            TokenType.KEY_WORD and tokens.peek().text == 'if')
    tokens.read()
    cond_smt = ASTnode(ASTtype.COND_SMT)
    cond = match_rel(tokens)
    if cond is None:
        show_error(tokens.peek().row_number, 'condition can\'t be null')
    if tokens.peek().type != TokenType.KEY_WORD or tokens.peek().text != 'then':
        show_error(tokens.peek().row_number, 'expect then after condition')

    tokens.read()

    child_smt = parse_statement(tokens)
    if child_smt is None:
        show_error(tokens.peek().row_number, 'expect at least one statement ~')
    cond_smt.COND_EXP = cond
    cond_smt.IF_SMT = []
    cond_smt.IF_SMT.append(child_smt)

    while tokens.peek().type != TokenType.KEY_WORD and tokens.peek().text != 'else':
        child_smt = parse_statement(tokens)
        if child_smt is None:
            break
        cond_smt.IF_SMT.append(child_smt)

    if tokens.peek().type == TokenType.KEY_WORD and tokens.peek().text == 'else':
        tokens.read()
        child_smt = ' '
        cond_smt.ELSE_SMT = []
        while tokens.peek().type != TokenType.KEY_WORD and tokens.peek().text != 'fi':
            # todo fix bug here,match failded triggered an error
            child_smt = parse_statement(tokens)
            if child_smt is None:
                break
            cond_smt.ELSE_SMT.append(child_smt)

    if tokens.peek().type != TokenType.KEY_WORD or tokens.peek().text != 'fi':
        show_error(tokens.peek().row_number,
                   'expect \'fi\' at the end of if statement~')
    tokens.read()
    return cond_smt


"""
parse declarations
"""


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
    scan(context)
    show_tokens(t_stream)
    # tok = read_type(t_stream)
    # draw_ast_tree(tok)
    node = parse_statement(t_stream)
    draw_ast_tree(node)
    print()
    # print(type([]))
    # print('~'*40)
    node2 = parse_statement(t_stream)
    draw_ast_tree(node2)
