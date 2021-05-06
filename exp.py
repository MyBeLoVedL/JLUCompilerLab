from typing import Text
from header import *
from header import ASTtype
import pprint as pp


def tok2val(tok: Token):
    if type(tok) is not Token:
        return tok
    if (tok.type == TokenType.NUM):
        return Value.INTEGER
    elif (tok.type == TokenType.ID):
        t = table[table_walk(tok.text)]
        if (t.type.type == TokenType.KEY_WORD and t.type.text == 'integer'):
            return Value.INTEGER
        elif (t.type.type == TokenType.KEY_WORD and t.type.text == 'char'):
            return Value.CHAR
    elif tok == 'integer':
        return Value.INTEGER
    elif tok == 'char':
        return Value.CHAR
    else:
        print("unknown value ")
        return None


def getval(node) -> Value:
    if type(node) is Token:
        return tok2val(node)
    elif type(node) is ASTnode:
        return node.value


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


def parse_id_list(tokens: TokenStream):
    res = []
    if tokens != TokenType.ID:
        show_error(tokens.peek().row_number, "expect at least one identifier~")

    res.append(tokens.read())
    while tokens == TokenType.COMMA:
        token_list_check(tokens, [TokenType.COMMA, TokenType.ID])
        tokens.read()
        res.append(tokens.read())
    return res


def token_list_check(tokens: TokenStream, target_list):
    l_len = len(target_list)

    for i in range(l_len):
        if type(target_list[i]) == str:
            if not (tokens.look_behind(i).type,
                    tokens.look_behind(i).text) == (TokenType.KEY_WORD,
                                                    target_list[i]):
                show_error(
                    tokens.look_behind(i).row_number,
                    f'expect {target_list[i]} here~ ')
            else:
                continue
        elif type(target_list[i]) is tuple:
            if not (tokens.look_behind(i).type is TokenType.KEY_WORD
                    and tokens.look_behind(i).text in target_list[i]):
                types = ' or '.join(target_list[i])
                show_error(
                    tokens.look_behind(i).row_number,
                    f'expect {types}  here~~ ')
            else:
                continue

        elif tokens.look_behind(i).type != target_list[i]:
            show_error(tokens.tokenStream[tokens.pos + i].row_number,
                       f'expect {str(target_list[i])} here~! ')


def match_id_more(tokens: TokenStream, id_name):
    tmp = None
    if tokens == TokenType.DOT:
        entry = table[table_walk(id_name)]
        if entry.type.type != ASTtype.RECORD:
            show_error(tokens.peek().row_number+1,
                       'can only extract field from record')

        tokens.read()
        token_list_check(tokens, [TokenType.ID])
        tmp = ASTnode(ASTtype.FIELD_VAR)
        tmp.FIELD = tokens.read().text
        if tmp.FIELD not in entry.type.VARIABLE:
            show_error(tokens.peek().row_number + 1,
                       'no such field')
        v = entry.type.VARIABLE[tmp.FIELD]
        if v == 'integer':
            tmp.value = Value.INTEGER
        elif v == 'char':
            tmp.value = Value.CHAR

    if tokens == TokenType.LEFT_SQUARE_BRACKET:
        entry = table[table_walk(id_name)]
        if entry.type.type != ASTtype.ARRAY:
            show_error(tokens.peek().row_number,
                       'can only apply index to array type')
        if tmp is None:
            tmp = ASTnode(ASTtype.INDEX_VAR)
        tokens.read()
        index = match_add(tokens)

        if index is None:
            show_error(tokens.peek().row_number + 1,
                       "expect a valid index here")
        try:
            i = int(index.text)
            if not (i >= int(entry.type.LOWER_BOUND.text) and i <= int(entry.type.UPPER_BOUND.text)):
                show_error(tokens.peek().row_number + 1,
                           'index must be in lower bound and upper bound')
        except:
            pass

        token_list_check(tokens, [TokenType.RIGHT_SQUARE_BRACKET])
        tokens.read()
        tmp.INDEX = index
        if entry.type.BASE_TYPE == 'integer':
            tmp.value = Value.INTEGER
        elif entry.type.BASE_TYPE == 'char':
            tmp.value = Value.CHAR
    return tmp


def match_pri(tokens: TokenStream):
    tmp = None
    init_pos = tokens.pos
    is_func = False
    if tokens == TokenType.ID:
        tmp = tokens.read()
        if (table_walk(tmp.text) < 0):
            show_error(tokens.peek().row_number,
                       f'symbol {tmp.text} with no definition')
        if tokens == TokenType.LEFT_PAREN:
            func_name = tmp
            tmp = ASTnode(ASTtype.FUNC_CALL)
            tmp.FUNC_NAME = func_name
            tokens.read()
            t = table[table_walk(func_name.text)]
            if type(t) != Sym_proc:
                show_error(tokens.peek().row_number,
                           'not a function to call')

            tmp.ARG_LIST = parse_arg_list(tokens)
            para_list = table[table_walk(func_name.text)].para
            if len(para_list) != len(tmp.ARG_LIST):
                show_error(tokens.peek().row_number,
                           'mismatched argument list number~')
            for i, pa in enumerate(tmp.ARG_LIST):
                if getval(pa) != getval(para_list[i][1]):
                    show_error(tokens.peek().row_number + 1,
                               f'mismatched parameter for function call~')
            expect(tokens, TokenType.RIGHT_PAREN, 'expect right parenthesis ~')
            is_func = True
        else:
            res = match_id_more(tokens, tmp.text)
            if res is not None:
                res.text = tmp.text
                tmp = res
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
    line = tokens.peek().row_number
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
            show_error(line,
                       'Expect expression after mul operator')
        if getval(left) != getval(right):
            show_error(tokens.peek().row_number+1,
                       'mismatched value type between left and right operand~')

        tmp.addChild(left)
        tmp.addChild(right)
        if getval(right) == Value.INTEGER:
            tmp.value = Value.INTEGER
        else:
            show_error(tokens.peek().row_number+1,
                       'only support integer operand now~')
        left = tmp
    return left


def match_add(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_mul(tokens)

    while tokens.not_empty() and (tokens.peek().type == TokenType.PLUS
                                  or tokens.peek().type == TokenType.MINUS):
        tmp = ASTnode(ASTtype.ADD_EXP)
        if tokens.peek().type == TokenType.PLUS:
            tmp.text = '+'
        else:
            tmp.text = '-'
        tokens.read()
        right = match_add(tokens)
        if right is None:
            show_error(tokens.tokenStream[tokens.pos - 1].row_number,
                       'Expect expression after plus operator')
        tmp = ASTnode(ASTtype.ADD_EXP)

        if getval(left) != getval(right):
            show_error(tokens.peek().row_number+1,
                       'mismatched value type between left and right operand~')

        if getval(right) == Value.INTEGER:
            tmp.value = Value.INTEGER
        else:
            show_error(tokens.peek().row_number+1,
                       'only support integer operand now~')
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_rel_low_priority(tokens: TokenStream):
    init_pos = tokens.pos

    left = match_add(tokens)

    while tokens.not_empty() and tokens.peek().type in (
            TokenType.LESS_THAN, TokenType.BIGGER_THAN,
            TokenType.LESS_THAN_OR_EQUAL, TokenType.BIGGER_THAN_OR_EQUAL):
        tmp = ASTnode(ASTtype.REL_EXP)
        if tokens.peek().type == TokenType.BIGGER_THAN:
            tmp.text = '>'
        elif tokens.peek().type == TokenType.LESS_THAN:
            tmp.text = '<'
        elif tokens.peek().type == TokenType.BIGGER_THAN_OR_EQUAL:
            tmp.text = '>='
        elif tokens.peek().type == TokenType.LESS_THAN_OR_EQUAL:
            tmp.text = '<='

        tokens.read()
        right = match_add(tokens)
        if right is None:
            show_error(tokens.tokenStream[tokens.pos].row_number,
                       'Expect expression after relational  operator')

        if getval(left) != getval(right):
            show_error(tokens.peek().row_number+1,
                       'mismatched value type between left and right operand~')

        if getval(right) == Value.INTEGER:
            tmp.value = Value.BOOLEAN
        else:
            show_error(tokens.peek().row_number+1,
                       'only support integer operand now~')

        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left


def match_rel(tokens: TokenStream):
    init_pos = tokens.pos
    left = match_rel_low_priority(tokens)

    while tokens.not_empty() and tokens.peek().type in (TokenType.EQUAL,
                                                        TokenType.NOT_EQUAL):
        tmp = ASTnode(ASTtype.REL_EXP)
        if tokens.peek().type == TokenType.EQUAL:
            tmp.text = '='
        elif tokens.peek().type == TokenType.NOT_EQUAL:
            tmp.text = '!='

        tokens.read()
        right = match_rel_low_priority(tokens)
        if right is None:
            show_error(tokens.tokenStream[tokens.pos].row_number,
                       'Expect expression after relational  operator')

        if getval(left) != getval(right):
            show_error(tokens.peek().row_number+1,
                       'mismatched value type between left and right operand~')

        if getval(right) in (Value.INTEGER, Value.BOOLEAN):
            tmp.value = Value.BOOLEAN
        else:
            show_error(tokens.peek().row_number+1,
                       'only support integer operand now~')
        tmp.addChild(left)
        tmp.addChild(right)
        left = tmp

    return left
