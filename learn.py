#!/bin/python3
import re
# percision = 10

# factor, sum = 2, 0

# for i in range(percision):
#     sum += 1.0 / factor
#     factor *= 2
#     print(f'{i}th iterration -> {sum}')


# def fib(bound):
#     a, b = 0, 1
#     for i in range(bound):
#         a, b = b, a+b
#         print(f'{i}th iteration -> {a}')


# subjects = ['Math', 'Chinese', 'English']


def examine():
    data = {}
    grades = []
    subjects = ['Math', 'Chinese', 'Englsih']
    while True:
        name = input('input the name of student >>> ')
        for lan in subjects:
            grades.append(int(input(f'input the grade of {lan}  >>>')))
        data[name] = grades[:]
        for name, grades in data.items():
            total_grade = sum(grades)
            if total_grade < 160:
                print(f"{name} has failed the exam")
            else:
                print(f"{name} has passed the exam")


def test_split():
    li = 'name altair  lee'.split(' ')
    print(li)


s = set([])

if __name__ == '__main__':
    # examine()
    # test_split()
    s = '.vscode/settings.json/.split /usr/include'
    print(s.split('/'))
    print(s.title())  # capitalize the first char in the string
    print(s.swapcase())  # only invole the alphabelt chars
    print(s.isalnum())
    print(':'.join(s.split('/')))  # used to change the dilimiter
    print(s.strip('.'))  # strip comibination of chars on the two sides
    print(s.find('code'))
    pattern = r'code'
    print(re.search(pattern, s).group(0))
    print(s.count('code'))
