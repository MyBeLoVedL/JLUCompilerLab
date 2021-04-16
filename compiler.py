#!/usr/bin/env python3

from lexer import scan
from header import *
from parser import __llparse, __lrparse
import abc


class Parser(metaclass=abc.ABCMeta):

    def reset(self, text):
        self.source = text
        self.pos = 0

    def tokenize(self) -> TokenStream:
        context = CharSequence(self.source)
        return scan(context)

    @abc.abstractclassmethod
    def parse(self, t_stream) -> ASTnode:
        pass

    def seman_check(root: ASTnode):
        pass

    def compile(self):
        t_stream = self.tokenize()
        root = self.parse(t_stream)
        self.seman_check(root)


class LLParser(Parser):
    def parse(self, t_stream) -> ASTnode:
        return __llparse(t_stream)


class LRParser(Parser):
    def parse(self, t_stream) -> ASTnode:
        return __lrparse(t_stream)


if __name__ == '__main__':
    source_text = ' iden.age[add(1 * 23)] := 1 + 2 > 3 +2;'
    parser = Parser(source_text)
    show_tokens(parser.tokenize())
    Parser()
    # set_text(source_text)
    # show_tokens(scan(CharSequence(source_text)))
    # parsed_text = source_text + '.'
    # context = CharSequence(parsed_text)
    # scan(context)
    # show_tokens(parser.tokenize())
