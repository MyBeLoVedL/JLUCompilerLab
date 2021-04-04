import header
import lexer
from header import Token
from header import TokenType
"""
parse expressions
"""
t_stream = header.TokenStream()
parameter_list = []


# 匹配失败 则回溯
def match_mul():
    global t_stream
    prime = t_stream.Token()
    if prime.type == TokenType.NUM:

    elif prime.type == TokenType.ID:

    elif prime.type == TokenType.LEFT_PAREN:

    else:
        lexer.show_error("error!")


def match_add():
    return


def match_rel():
    return


def match_logic():
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



