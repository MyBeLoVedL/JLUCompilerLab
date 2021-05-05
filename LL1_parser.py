import copy
ultiSym = []
unultiSym = []
syntaxQueue = []
production = []
predict = []


symName = {'=':'EQ',
            '<':'LT',
            '+':'PLUS',
            '-':'MINUS',
	        '*':'TIMES',
            '/':'OVER',
            '[':'LPAREN',
            ']':'RPAREN',
            '.':'DOT',
            ';':'SEMI',
	        ',':'COMMA',
            '(':'LMIDPAREN',
            ')':'RMIDPAREN',
            ':=':'ASSIGN',
            '..':'UNDERANGE'
}


def getSym():
    global ultiSym, unultiSym
    ultiSym = open('ultiSym.txt').read().split()
    ultiSym = [sym[:-1] if sym[len(sym)-1] == ',' else sym for sym in ultiSym]

    unultiSym = open('unultiSym.txt').read().split()
    unultiSym = [sym[:-1] if sym[len(sym)-1] == ',' else sym for sym in unultiSym]


def getProduction():
    global production
    production = []
    f = open('production.txt')
    lines = f.readlines()
    lines = [l for l in lines if l != '\n']

    left = ""
    for l in lines:
        l = l.strip()
        if '::=' in l:
            l = l.split('::=')
            left = l[0].strip()
            right = l[1].split()
        else:
            right = l.split('|')[1].split()
        production.append((left,tuple(right)))


def getPredict():
    global predict
    predict = open('predict.txt').readlines()
    predict = [line.strip().split(',') for line in predict]


def getDerive():
    global derive
    for word in unultiSym:
        for token in ultiSym:
            for i in range(len(production)):
                prod = production[i]
                if prod[0] == word and len([t for t in predict[i] if match(t,token) == True]) != 0:
                    derive[(word,token)] = prod[1]


def match(curSym,tokenSym):
    if curSym == tokenSym: return True
    tcurSym = copy.deepcopy(curSym); ttokenSym = copy.deepcopy(tokenSym)
    if tcurSym in symName: tcurSym = symName[curSym]
    if tcurSym == ttokenSym: return True
    if ttokenSym in ultiSym: ttokenSym =tokenSym.lower()
    return True if tcurSym == ttokenSym else False