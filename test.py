#!/usr/bin/env python3


from pprint import pprint
from collections import deque
from typing import Any
import heapq


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


def search(text, pat, n):
    context = deque(maxlen=n)
    for line in text:
        if pat in line:
            yield line, context
        context.append(line)


class pq():
    def __init__(self):
        self.Q = []
        self.I = 0

    def push(self, item, pri):
        heapq.heappush(self.Q, (-pri, self.I, item))
        self.I += 1

    def pop(self):
        return heapq.heappop(self.Q)[-1]


if __name__ == '__main__':
    # s = Stu('altair')
    # s.age = 20
    # print(s.gender)
    # s.gender = 'unknown'
    # pprint(s.__dict__)

    pq = pq()
    pq.push("altair", 10)
    pq.push("veaga", 12)
    pq.push("Sirus", 2)
    print(pq.Q)
