#!/usr/bin/env python3


from pprint import pprint
from collections import deque
import heapq
import abc


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


class Animal():
    def __init__(self, name) :
        self.name = name

    @abc.abstractmethod
    def tell(self):
        # print("I am animal")
        pass


class Man(Animal):
    # def __init__(self, name, gender):
    #     super().__init__(name)
    #     self.gender = gender

    def tell(self):
        print("I am man")


if __name__ == '__main__':
    # s = Stu('altair')
    # s.age = 20
    # print(s.gender)
    # s.gender = 'unknown'
    # pprint(s.__dict__)

    a = Man('altair')
    a.tell()
    # b = Animal('vvvvv')
    # b.tell()
    # pq = pq()
    # pq.push("altair", 10)
    # pq.push("veaga", 12)
    # pq.push("Sirus", 2)
    # print(pq.Q)

'''
阶段测试结果（词法分析 + 递归下降）
# program begin之间 如果是关键字错误如ty，也会提示expect begin
# 中文字符 会爆红宕机
# 自定义类型 数字和非法字符开头可以报错，但字母开头如charchar，则可以成功识别不报错
# 自定义类型 使用未定义类型，如tt而t不报错
# 自定义类型 拼写错误 integet不报错
# 分号是semi_colon 不是 colon
# 识别数组 
# 运算符 +* 不报错
# write关键字的识别 拼写错误wrie不报错

'''