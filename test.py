a = {'element, 1': 1, 'square, 2': 4}
b = ', '.join(map(str, list(a.keys()))).split(', ')

for i in b:
    print(i, type(i))