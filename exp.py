
from header import *
from header import ASTtype


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
