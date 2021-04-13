#!/usr/bin/env python3


from pprint import pprint

from typing import Any


class Stu:
    gender = 'female'

    def __init__(self, name):
        self.name = name

    # def __getattribute__(self, name: str):
    #     return 'bula'

    def __getattr__(self, attr):
        print('accessing attribute')
        # return 'male'
        # return self.__dict__[attr].upper()

    def __setattr__(self, name: str, value: Any) -> None:
        print('setting attribute')


if __name__ == '__main__':
    # s = Stu('altair')
    # s.age = 20
    # print(s.gender)
    # s.gender = 'unknown'
    # pprint(s.__dict__)

    dir(int)
