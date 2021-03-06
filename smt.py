from header import *
from exp import *


def parse_statement(tokens: TokenStream):
    if tokens == 'return':
        return parse_return_statement(tokens)
    elif tokens == 'if':
        return parse_condition_statement(tokens)
    elif tokens == 'while':
        return parse_loop_statement(tokens)
    elif tokens == 'read' or tokens == 'write':
        return parse_IO_statement(tokens)
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

    if table_walk(asg_smt.VARI.text) < 0:
        show_error(tokens.tokenStream[tokens.pos - 1].row_number,
                   f'symbol {asg_smt.VARI.text} with no definition')

    res = match_id_more(tokens, asg_smt.VARI.text)
    if res is not None:
        res.text = asg_smt.VARI.text
        asg_smt.VARI = res

    if tokens.peek().type != TokenType.ASSIGN:
        tokens.pos = init_pos
        return None

    t = table[table_walk(asg_smt.VARI.text)]
    if type(t) != Sym_vari:
        show_error(
            tokens.tokenStream[tokens.pos].row_number, 'only variable can be left value')
    expect(tokens, TokenType.ASSIGN, 'expect assign operator ~')

    val = match_rel(tokens)
    if val is None:
        show_error(
            tokens.tokenStream[tokens.pos].row_number, 'expect expression after assign')

    if getval(val) != getval(asg_smt.VARI):
        show_error(tokens.peek().row_number + 1,
                   'incompatible value for assignment')
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
    if tokens == 'write':
        io_smt = ASTnode(ASTtype.OUTPUT_SMT)
    else:
        io_smt = ASTnode(ASTtype.INPUT_SMT)
    tokens.read()
    token_list_check(tokens, [
        TokenType.LEFT_PAREN])
    tokens.read()

    id = tokens.read()
    more = match_id_more(tokens, id.text)
    if more is not None:
        more.text = id.text
        id = more

    if id is None:
        show_error(tokens.peek().row_number, "expect valid value~")

    io_smt.addChild(id)
    token_list_check(tokens, [TokenType.RIGHT_PAREN, TokenType.COLON])
    tokens.read()
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
    if cond.type != ASTtype.REL_EXP:
        show_error(tokens.peek().row_number, 'expect an boolean tester')
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

    token_list_check(tokens, ['endwh', TokenType.COLON])
    tokens.read()
    tokens.read()
    return loop_smt


def parse_condition_statement(tokens: TokenStream):
    assert (tokens.peek().type ==
            TokenType.KEY_WORD and tokens.peek().text == 'if')
    tokens.read()
    cond_smt = ASTnode(ASTtype.COND_SMT)
    cond = match_rel(tokens)
    if cond is None:
        show_error(tokens.peek().row_number, 'condition can\'t be null')
    if cond.type != ASTtype.REL_EXP:
        show_error(tokens.peek().row_number, 'expect an boolean tester')
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

    token_list_check(tokens, ['fi', TokenType.COLON])
    tokens.read()
    tokens.read()
    return cond_smt
