#!/usr/bin/env python3


"""
parse expressions
"""
from header import *
from lexer import *

source_text = ''


def expect(tokens, target_token_type, error_msg):
    if tokens.peek().type != target_token_type:
        show_error(tokens.peek().row_number, error_msg)
    tokens.read()


def match_pri(tokens: TokenStream):
    tmp = ''
    init_pos = tokens.pos
    if not tokens.not_empty():
        return
    if tokens.peek().type == TokenType.ID:
        tmp = tokens.read()
        if tokens.peek().type == TokenType.LEFT_PAREN:
            func_name = tmp
            tmp = ASTnode(ASTtype.FUNC_CALL)
            tmp.FUNC_NAME = func_name
            tmp.ARG_LIST = []
            tokens.read()
            if tokens.peek().type != TokenType.RIGHT_PAREN:
                first_arg = match_rel(tokens)
                tmp.ARG_LIST.append(first_arg)
            while tokens.peek().type != TokenType.RIGHT_PAREN:
                expect(tokens, TokenType.COMMA,
                       'use comma to seperate multiple arguments ~')
                arg = match_rel(tokens)
                tmp.ARG_LIST.append(arg)
            expect(tokens, TokenType.RIGHT_PAREN, 'expect right parenthesis ~')
    elif tokens.peek().type == TokenType.NUM:
        tmp = tokens.read()
    elif tokens.peek().type == TokenType.LEFT_PAREN:
        tokens.read()
        child = match_rel(tokens)
        if child is None:
            tokens.reset_pos(init_pos)
            return child
        if tokens.peek().type != TokenType.RIGHT_PAREN:
            show_error(
                tokens.tokenStream[tokens.pos].row_number, 'mis-matched parenthesis~')
        else:
            tmp = child
            tokens.read()
    return tmp


def match_mul(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_pri(tokens)

    while tokens.not_empty() and (tokens.peek().type == TokenType.STAR or tokens.peek().type == TokenType.DIV):
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


def parse_assign_statement(tokens: TokenStream):
    return None


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
    source_text = 'add(1 + 2,1*2 );\nif 1 > 2 then a = 10; else a = 20; fi'
    set_text(source_text)
    parsed_text = source_text + '.'
    context = CharSequence(parsed_text)
    scan(context)
    show_tokens(t_stream)
    node = parse_statement(t_stream)
    draw_ast_tree(node)
    print()
    print('~'*40)
    node2 = parse_statement(t_stream)
    draw_ast_tree(node2)
