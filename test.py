import header
s = 'abc'
b = header.Token()
if type(b) == header.TokenStream:
    print('I am str')
else:
    print('I am not str')

